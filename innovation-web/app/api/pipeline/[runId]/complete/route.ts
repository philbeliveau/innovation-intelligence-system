import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { completeSchema } from '@/lib/validations/webhook'

interface OpportunityPayload {
  number?: number
  title: string
  markdown?: string
  fullContent?: string  // Backend sends this field name
  content?: string
}

/**
 * Sanitize opportunity content by removing stage outputs and JSON if present
 * Backend sometimes sends stage outputs concatenated with the actual spark markdown
 */
function sanitizeOpportunityContent(rawContent: string): string {
  // Pattern 1: Remove stage output JSON blocks (e.g., "stage1_output": "{...}")
  // This handles the case where all stage outputs are concatenated together
  let cleaned = rawContent

  // Remove all stage output JSON blocks
  const stageOutputPattern = /"stage\d+_output":\s*"[^"]*(?:\\.[^"]*)*"/g
  cleaned = cleaned.replace(stageOutputPattern, '')

  // Remove other common JSON fields that might be prepended
  const jsonFieldPatterns = [
    /"(?:trendTitle|trendImage|coreMechanism|businessImpact|patternTransfersTo|mechanisms|abstractionTest|evidenceStrength|cpgRelevance|extractedText|brand_profile|research_data)":\s*(?:"[^"]*(?:\\.[^"]*)*"|\[[^\]]*\]|\{[^}]*\})/g,
  ]

  jsonFieldPatterns.forEach(pattern => {
    cleaned = cleaned.replace(pattern, '')
  })

  // Remove JSON structural characters that might be left over
  cleaned = cleaned
    .replace(/^\s*[\{\},"]*\s*/, '') // Remove leading JSON chars
    .replace(/\s*[\{\},"]*\s*$/, '') // Remove trailing JSON chars
    .replace(/\\n/g, '\n')           // Convert literal \n to actual newlines
    .replace(/\\"/g, '"')            // Convert escaped quotes
    .replace(/\n{3,}/g, '\n\n')      // Collapse multiple newlines
    .trim()

  // If the cleaned content is empty or still looks like JSON, return empty
  // (Better to have no content than malformed content)
  if (cleaned.length === 0 || cleaned.startsWith('{') || cleaned.startsWith('"')) {
    console.warn('[Sanitize] Content appears to be pure JSON after cleaning, returning empty')
    return ''
  }

  // Verify the result looks like markdown (should start with # or regular text)
  if (!cleaned.startsWith('#') && !/^[A-Za-z]/.test(cleaned)) {
    console.warn('[Sanitize] Content does not look like markdown after cleaning')
    return ''
  }

  return cleaned
}

/**
 * POST /api/pipeline/[runId]/complete
 *
 * Webhook endpoint called by Railway backend when pipeline completes.
 * Updates run status, saves opportunity cards, and creates inspiration report.
 *
 * Authentication: X-Webhook-Secret header
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    // 1. Authenticate webhook using shared secret
    const webhookSecret = request.headers.get('X-Webhook-Secret')
    const expectedSecret = process.env.WEBHOOK_SECRET

    if (!expectedSecret) {
      console.error('[Webhook] WEBHOOK_SECRET environment variable is not set')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    if (webhookSecret !== expectedSecret) {
      console.error('[Webhook] Authentication failed: Invalid secret')
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 2. Extract runId from params and body
    const { runId } = await params
    const body = await request.json()

    // 3. Validate payload using Zod schema
    const validationResult = completeSchema.safeParse(body)
    if (!validationResult.success) {
      console.error('[Webhook] Validation failed:', validationResult.error.format())
      return NextResponse.json(
        {
          error: 'Invalid payload',
          details: validationResult.error.format()
        },
        { status: 400 }
      )
    }

    const { completedAt, duration, opportunities, fullReportMarkdown } = validationResult.data

    console.log(`[Webhook] Received completion for run ${runId}`)

    // 4. Verify run exists and get current status
    const existingRun = await prisma.pipelineRun.findUnique({
      where: { id: runId },
      include: {
        opportunityCards: true,
        inspirationReport: true
      }
    })

    if (!existingRun) {
      console.error(`[Webhook] Run not found: ${runId}`)
      return NextResponse.json(
        { error: 'Run not found' },
        { status: 404 }
      )
    }

    // 5. Handle idempotency - if already completed, return success
    if (existingRun.status === 'COMPLETED') {
      console.log(`[Webhook] Run ${runId} already completed (idempotent)`)
      return NextResponse.json({
        success: true,
        message: 'Run already completed'
      })
    }

    // 6. Update run status to COMPLETED and save fullReportMarkdown if provided
    const updateData: {
      status: 'COMPLETED'
      completedAt: Date
      duration?: number
      fullReportMarkdown?: string
    } = {
      status: 'COMPLETED',
      completedAt: completedAt ? new Date(completedAt) : new Date(),
      duration
    }

    // Add fullReportMarkdown if provided (backward compatibility)
    if (fullReportMarkdown) {
      updateData.fullReportMarkdown = fullReportMarkdown
      console.log(`[Webhook] Saving fullReportMarkdown (${fullReportMarkdown.length} chars)`)
    }

    try {
      await prisma.pipelineRun.update({
        where: { id: runId },
        data: updateData
      })
      console.log(`[Webhook] Updated run ${runId} status to COMPLETED`)
    } catch (updateError) {
      console.error(`[Webhook] Failed to update run status:`, updateError)
      // Don't fail the webhook - try to save opportunity cards anyway
    }

    // 7. Save opportunity cards (validate required fields)

    console.log(`[Webhook] Received ${opportunities.length} opportunities for run ${runId}`)
    console.log(`[Webhook] First opportunity sample:`, JSON.stringify(opportunities[0], null, 2))

    // Filter and map valid opportunities
    const validOpportunities = opportunities
      .map((opp, idx) => ({
        opp,
        index: idx
      }))
      .filter(({ opp }) => {
        if (!opp.title) {
          console.warn(`[Webhook] Skipping opportunity ${opp.number || 'unknown'} - missing title`)
          return false
        }
        // Check for content in any of the three possible field names
        if (!opp.markdown && !opp.fullContent && !opp.content) {
          console.warn(`[Webhook] Skipping opportunity ${opp.number || 'unknown'} "${opp.title}" - missing markdown/fullContent/content`)
          return false
        }
        return true
      })
      .map(({ opp, index }) => {
        // Get raw content from any available field
        const rawContent = opp.fullContent || opp.markdown || opp.content || ''

        // Sanitize content to remove JSON prefix if present
        const cleanContent = sanitizeOpportunityContent(rawContent)

        console.log(`[Webhook] Opportunity ${opp.number || index + 1}: Raw length=${rawContent.length}, Clean length=${cleanContent.length}`)

        return {
          runId,
          number: opp.number || index + 1,
          title: opp.title,
          content: cleanContent,
          isStarred: false
        }
      })

    console.log(`[Webhook] Validated ${validOpportunities.length}/${opportunities.length} opportunities for database insertion`)

    let cardsCreated = 0
    try {
      // Bulk insert all valid cards in single transaction
      const result = await prisma.opportunityCard.createMany({
        data: validOpportunities,
        skipDuplicates: true
      })
      cardsCreated = result.count
    } catch (cardError) {
      console.error(`[Webhook] Failed to bulk create cards:`, cardError)
      // Fallback to individual creation if bulk insert fails
      for (const cardData of validOpportunities) {
        try {
          await prisma.opportunityCard.create({ data: cardData })
          cardsCreated++
        } catch (individualError) {
          console.error(`[Webhook] Failed to create individual card ${cardData.number}:`, individualError)
        }
      }
    }

    console.log(`[Webhook] Created ${cardsCreated}/${opportunities.length} opportunity cards`)

    // 8. Fetch stage outputs from StageOutput table and create InspirationReport
    try {
      // Get all stage outputs from database (already saved by backend during pipeline execution)
      const stageOutputs = await prisma.stageOutput.findMany({
        where: { runId },
        orderBy: { stageNumber: 'asc' }
      })

      console.log(`[Webhook] Found ${stageOutputs.length} stage outputs in database`)

      // Map stage outputs by stage number
      const stageMap = new Map<number, string>()
      stageOutputs.forEach(stage => {
        stageMap.set(stage.stageNumber, stage.output)
      })

      // Extract track titles from stage 1 if available
      let selectedTrack = ""
      let nonSelectedTrack = ""

      const stage1Output = stageMap.get(1)
      if (stage1Output) {
        try {
          const stage1Data = JSON.parse(stage1Output)
          selectedTrack = stage1Data.inspirations?.[0]?.title || stage1Data.trendTitle || ""
          nonSelectedTrack = stage1Data.inspirations?.[1]?.title || ""
        } catch (e) {
          console.warn(`[Webhook] Could not parse stage 1 output for track titles`)
        }
      }

      // Create inspiration report with stage outputs from database
      await prisma.inspirationReport.create({
        data: {
          runId,
          selectedTrack,
          nonSelectedTrack,
          stage1Output: stageMap.get(1) || "",
          stage2Output: stageMap.get(2) || "",
          stage3Output: stageMap.get(3) || "",
          stage4Output: stageMap.get(4) || "",
          stage5Output: stageMap.get(5) || ""
        }
      })
      console.log(`[Webhook] Created inspiration report for run ${runId}`)
    } catch (reportError) {
      console.error(`[Webhook] Failed to create inspiration report:`, reportError)
      // Don't fail the entire webhook if report creation fails
    }

    console.log(`[Webhook] Pipeline ${runId} completed successfully: ${cardsCreated} cards saved`)

    return NextResponse.json({
      success: true,
      cardsCreated,
      totalOpportunities: opportunities.length
    })

  } catch (error) {
    console.error('[Webhook] Error processing completion:', error)

    // Log detailed error information
    if (error instanceof Error) {
      console.error('[Webhook] Error name:', error.name)
      console.error('[Webhook] Error message:', error.message)
      console.error('[Webhook] Error stack:', error.stack)
    }

    return NextResponse.json(
      {
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

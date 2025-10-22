import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

interface OpportunityPayload {
  number?: number
  title: string
  markdown: string
  content?: string
}

/**
 * POST /api/runs/[runId]/complete
 *
 * Webhook endpoint called by Railway backend when pipeline completes.
 * Updates run status, saves opportunity cards, and creates inspiration report.
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

    console.log(`[Webhook] Received completion for run ${runId}`)

    // 3. Verify run exists and get current status
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

    // 4. Handle idempotency - if already completed, return success
    if (existingRun.status === 'COMPLETED') {
      console.log(`[Webhook] Run ${runId} already completed (idempotent)`)
      return NextResponse.json({
        success: true,
        message: 'Run already completed'
      })
    }

    // 5. Update run status to COMPLETED
    await prisma.pipelineRun.update({
      where: { id: runId },
      data: {
        status: 'COMPLETED',
        completedAt: new Date(body.completedAt),
        duration: body.duration
      }
    })

    console.log(`[Webhook] Updated run ${runId} status to COMPLETED`)

    // 6. Save opportunity cards (validate required fields)
    const opportunities = (body.opportunities || []) as OpportunityPayload[]

    // Filter and map valid opportunities
    const validOpportunities = opportunities
      .map((opp, idx) => ({
        opp,
        index: idx
      }))
      .filter(({ opp }) => {
        if (!opp.title || !opp.markdown) {
          console.warn(`[Webhook] Skipping opportunity with missing fields:`, opp)
          return false
        }
        return true
      })
      .map(({ opp, index }) => ({
        runId,
        number: opp.number || index + 1,
        title: opp.title,
        content: opp.markdown || opp.content || '',
        isStarred: false
      }))

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

    // 7. Save stage outputs as InspirationReport
    const stages = body.stageOutputs || {}

    try {
      await prisma.inspirationReport.create({
        data: {
          runId,
          selectedTrack: stages.stage1?.inspirations?.[0]?.title || "",
          nonSelectedTrack: stages.stage1?.inspirations?.[1]?.title || "",
          stage1Output: JSON.stringify(stages.stage1 || {}),
          stage2Output: JSON.stringify(stages.stage2 || {}),
          stage3Output: JSON.stringify(stages.stage3 || {}),
          stage4Output: JSON.stringify(stages.stage4 || {}),
          stage5Output: JSON.stringify(stages.stage5 || {})
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

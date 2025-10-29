import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * GET /api/pipeline/[runId]/status
 *
 * Retrieves the current status of a pipeline run from Prisma database.
 * This endpoint now reads ONLY from Prisma (no Railway backend calls).
 *
 * The Python backend updates Prisma via POST /api/pipeline/[runId]/stage-update
 *
 * Response:
 * {
 *   run_id: string
 *   status: 'PROCESSING' | 'COMPLETED' | 'FAILED'
 *   current_stage: 0-5  (highest stage number with data)
 *   stages: {
 *     "1": { status: "COMPLETED", output: {...}, completed_at: "..." }
 *     "2": { status: "PROCESSING", ... }
 *     ...
 *   }
 *   brand_name?: string (companyName from run)
 *   // NEW FIELDS (Story 10.5)
 *   stage1Output?: { extractedText: string, mechanisms: array } | null
 *   stage2Output?: { signals: array } | null
 *   stage3Output?: { insights: array } | null
 *   stage4Output?: { preliminary: array } | null
 *   hasFullReport: boolean
 * }
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    // Extract runId from URL parameter
    const { runId } = await params

    // Sanitize runId to prevent injection attacks
    const sanitizedRunId = runId.replace(/[^a-z0-9-]/gi, '')
    if (sanitizedRunId !== runId) {
      return NextResponse.json(
        { error: 'Invalid run ID format' },
        { status: 400 }
      )
    }

    console.log(`[API /pipeline/status] Fetching status for run: ${sanitizedRunId}`)

    // Fetch run with all stage outputs and opportunity cards from Prisma
    // Story 10.5: Added stage JSON fields and fullReportMarkdown for retrospective mode
    const run = await prisma.pipelineRun.findUnique({
      where: { id: sanitizedRunId },
      select: {
        id: true,
        status: true,
        companyName: true,
        // NEW FIELDS (Story 10.5) - JSON stage outputs for retrospective mode
        stage1Output: true,
        stage2Output: true,
        stage3Output: true,
        stage4Output: true,
        fullReportMarkdown: true,
        // Relations
        stageOutputs: {
          orderBy: { stageNumber: 'asc' }
        },
        opportunityCards: {
          orderBy: { number: 'asc' }
        }
      }
    })

    if (!run) {
      console.log(`[API /pipeline/status] Run not found: ${sanitizedRunId}`)
      return NextResponse.json(
        { error: 'Run ID not found' },
        { status: 404 }
      )
    }

    // Build stages object keyed by stage number
    const stages: Record<string, unknown> = {}
    let currentStage = 0

    // Initialize all 5 stages as pending
    for (let i = 1; i <= 5; i++) {
      stages[i.toString()] = { status: 'pending' }
    }

    // Populate with actual stage data from database
    for (const stageOutput of run.stageOutputs) {
      const stageKey = stageOutput.stageNumber.toString()

      // Parse output as JSON if it's a JSON string
      let parsedOutput: unknown
      try {
        parsedOutput = JSON.parse(stageOutput.output)
      } catch {
        // If not JSON, use as-is (markdown or plain text)
        parsedOutput = stageOutput.output
      }

      stages[stageKey] = {
        status: stageOutput.status.toLowerCase(), // "COMPLETED" → "completed"
        output: parsedOutput,
        completed_at: stageOutput.completedAt?.toISOString() || null
      }

      // Track highest stage number we have data for
      if (stageOutput.stageNumber > currentStage) {
        currentStage = stageOutput.stageNumber
      }
    }

    // If no stages have started yet, current_stage should be 0
    if (run.stageOutputs.length === 0) {
      currentStage = 0
    }

    // Build partial opportunities array for Stage 5
    let partialOpportunities: Array<{
      id: string
      number: number
      title: string
      summary: string
      heroImageUrl: string | null
      isComplete: boolean
    }> | undefined

    // Include partial opportunities if Stage 5 is processing or completed
    const stage5 = run.stageOutputs.find(s => s.stageNumber === 5)
    if (stage5 && run.opportunityCards.length > 0) {
      partialOpportunities = run.opportunityCards.map(card => ({
        id: card.id,
        number: card.number,
        title: card.title,
        summary: card.content.substring(0, 200) + (card.content.length > 200 ? '...' : ''),
        heroImageUrl: null, // TODO: Add hero image support in future
        isComplete: run.status === 'COMPLETED'
      }))
    }

    // Build response matching Railway backend format
    // Story 10.5: Added stage output JSON fields and hasFullReport flag
    const response = {
      run_id: run.id,
      status: run.status.toLowerCase(), // "PROCESSING" → "processing"
      current_stage: currentStage,
      stages,
      brand_name: run.companyName,
      ...(partialOpportunities && { partialOpportunities }),
      // NEW FIELDS (Story 10.5) - Retrospective mode support
      stage1Output: run.stage1Output,
      stage2Output: run.stage2Output,
      stage3Output: run.stage3Output,
      stage4Output: run.stage4Output,
      hasFullReport: !!run.fullReportMarkdown
    }

    console.log(`[API /pipeline/status] Returning status: ${run.status}, current_stage: ${currentStage}, hasFullReport: ${!!run.fullReportMarkdown}`)

    return NextResponse.json(response)

  } catch (error) {
    console.error('[API /pipeline/status] Unexpected error:', error)

    if (error instanceof Error) {
      console.error('[API /pipeline/status] Error details:', error.message)
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

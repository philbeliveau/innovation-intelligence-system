import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * GET /api/pipeline/[runId]/opportunity-cards
 *
 * Retrieves all opportunity cards (sparks) for a completed pipeline run.
 * This endpoint is called by PipelineViewer after pipeline completion.
 *
 * Response:
 * {
 *   opportunityCards: [
 *     {
 *       id: string
 *       number: number
 *       title: string
 *       summary: string
 *       content: string
 *       createdAt: string
 *     }
 *   ]
 * }
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { runId } = await params

    // Sanitize runId to prevent injection attacks
    const sanitizedRunId = runId.replace(/[^a-z0-9-]/gi, '')
    if (sanitizedRunId !== runId) {
      return NextResponse.json(
        { error: 'Invalid run ID format' },
        { status: 400 }
      )
    }

    console.log(`[API /opportunity-cards] Fetching cards for run: ${sanitizedRunId}`)

    // Verify the pipeline run exists
    const run = await prisma.pipelineRun.findUnique({
      where: { id: sanitizedRunId }
    })

    if (!run) {
      console.log(`[API /opportunity-cards] Run not found: ${sanitizedRunId}`)
      return NextResponse.json(
        { error: 'Pipeline run not found' },
        { status: 404 }
      )
    }

    // Fetch all opportunity cards for this run
    const cards = await prisma.opportunityCard.findMany({
      where: { runId: sanitizedRunId },
      orderBy: { number: 'asc' },
      select: {
        id: true,
        number: true,
        title: true,
        content: true,
        createdAt: true
      }
    })

    console.log(`[API /opportunity-cards] Found ${cards.length} cards for run: ${sanitizedRunId}`)

    // Transform cards to match expected interface
    const opportunityCards = cards.map(card => ({
      id: card.id,
      number: card.number,
      title: card.title,
      summary: card.content.substring(0, 200) + (card.content.length > 200 ? '...' : ''),
      content: card.content,
      createdAt: card.createdAt.toISOString()
    }))

    return NextResponse.json({
      opportunityCards
    })

  } catch (error) {
    console.error('[API /opportunity-cards] Unexpected error:', error)

    if (error instanceof Error) {
      console.error('[API /opportunity-cards] Error details:', error.message)
    }

    return NextResponse.json(
      { error: 'Failed to fetch opportunity cards' },
      { status: 500 }
    )
  }
}

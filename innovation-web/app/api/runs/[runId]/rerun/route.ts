import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'

/**
 * POST /api/runs/[runId]/rerun - Rerun a pipeline with same settings
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const { runId } = await params

    // In a real implementation:
    // 1. Fetch original run details from database
    // 2. Get the original document blob URL
    // 3. Create a new run with same settings
    // 4. Trigger the pipeline with the new run ID

    // For now, generate a new run ID and return it
    const newRunId = `run-${Date.now()}`

    console.log(`[API /runs/:id/rerun] Rerunning ${runId} as ${newRunId}`)

    // In production, this would trigger the actual pipeline
    // and create database records

    return NextResponse.json({
      success: true,
      newRunId,
      message: 'Pipeline rerun initiated',
    })
  } catch (error) {
    console.error('[API /runs/:id/rerun] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

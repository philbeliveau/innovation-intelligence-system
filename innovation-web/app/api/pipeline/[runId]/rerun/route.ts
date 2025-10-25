import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'
import { runPipeline } from '@/lib/backend-client'

/**
 * POST /api/pipeline/[runId]/rerun - Rerun a pipeline with same settings
 *
 * Creates a new run with same document and company, triggers Railway backend
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

    // 1. Fetch original run with user relation for authorization
    const originalRun = await prisma.pipelineRun.findUnique({
      where: { id: runId },
      include: {
        user: true
      }
    })

    if (!originalRun) {
      return NextResponse.json(
        { error: 'Original run not found' },
        { status: 404 }
      )
    }

    // 2. CRITICAL: Verify user owns the original run
    if (originalRun.user.clerkId !== userId) {
      return NextResponse.json(
        { error: 'Unauthorized - you do not own this run' },
        { status: 403 }
      )
    }

    // 3. Create new run record with "(rerun)" suffix
    // IMPORTANT: Preserve exact same parameters but mark as new run
    const newRun = await prisma.pipelineRun.create({
      data: {
        userId: originalRun.userId, // Maintain same owner
        companyName: originalRun.companyName, // Exact same company
        documentName: `${originalRun.documentName} (rerun)`, // Append suffix
        documentUrl: originalRun.documentUrl, // REUSE blob URL (no re-upload)
        pipelineVersion: originalRun.pipelineVersion, // Same pipeline version
        status: 'PROCESSING', // Start as processing
        // Note: Do NOT copy completedAt, duration, or results
      }
    })

    console.log(`[API /pipeline/:id/rerun] Created rerun ${newRun.id} from original ${runId}`)

    // 4. Trigger Railway backend with new run ID but original document
    try {
      // Extract companyId from company name
      // TODO: Store companyId in database schema for better reliability
      const companyId = originalRun.companyName.toLowerCase().includes('lactalis')
        ? 'lactalis-canada'
        : 'default-company'

      await runPipeline(originalRun.documentUrl || '', companyId)

      console.log(`[API /pipeline/:id/rerun] Successfully triggered Railway backend for ${newRun.id}`)

      return NextResponse.json({
        success: true,
        newRunId: newRun.id,
        message: 'Pipeline rerun initiated',
      })
    } catch (backendError) {
      // 5. If Railway trigger fails, mark new run as FAILED
      await prisma.pipelineRun.update({
        where: { id: newRun.id },
        data: {
          status: 'FAILED',
          completedAt: new Date(),
          // TODO: Add errorMessage field to schema for detailed error tracking
        }
      })

      console.error('[API /pipeline/:id/rerun] Railway backend trigger failed:', backendError)

      return NextResponse.json(
        { error: 'Failed to start pipeline rerun. The run has been marked as failed.' },
        { status: 500 }
      )
    }
  } catch (error) {
    console.error('[API /pipeline/:id/rerun] Unexpected error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

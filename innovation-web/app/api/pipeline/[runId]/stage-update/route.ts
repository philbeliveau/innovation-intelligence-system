import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { RunStatus } from '@prisma/client'

/**
 * POST /api/pipeline/[runId]/stage-update
 *
 * Internal endpoint for Railway backend to update stage progress in Prisma.
 * This replaces the file-based /tmp/runs/{runId}/status.json approach.
 *
 * Authentication: X-Webhook-Secret header (same as complete webhook)
 *
 * Request body:
 * {
 *   stageNumber: 1-5,
 *   stageName: "Input Processing" | "Signal Amplification" | etc,
 *   status: "PROCESSING" | "COMPLETED" | "FAILED",
 *   output: "stage output data (JSON or markdown)",
 *   completedAt?: ISO timestamp (optional, for completed stages)
 * }
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
      console.error('[StageUpdate] WEBHOOK_SECRET environment variable is not set')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    if (webhookSecret !== expectedSecret) {
      console.error('[StageUpdate] Authentication failed: Invalid secret')
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 2. Extract runId and request body
    const { runId } = await params
    const body = await request.json()
    const { stageNumber, stageName, status, output, completedAt } = body

    // 3. Validate required fields
    if (!stageNumber || !stageName || !status) {
      return NextResponse.json(
        { error: 'Missing required fields: stageNumber, stageName, status' },
        { status: 400 }
      )
    }

    // Validate stageNumber range
    if (stageNumber < 1 || stageNumber > 5) {
      return NextResponse.json(
        { error: 'stageNumber must be between 1 and 5' },
        { status: 400 }
      )
    }

    // Validate status enum
    if (!['PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'].includes(status)) {
      return NextResponse.json(
        { error: 'Invalid status value' },
        { status: 400 }
      )
    }

    console.log(`[StageUpdate] Updating run ${runId} stage ${stageNumber} to ${status}`)

    // 4. Verify run exists
    const existingRun = await prisma.pipelineRun.findUnique({
      where: { id: runId }
    })

    if (!existingRun) {
      console.error(`[StageUpdate] Run not found: ${runId}`)
      return NextResponse.json(
        { error: 'Run not found' },
        { status: 404 }
      )
    }

    // 5. Upsert StageOutput record (create or update)
    const stageOutput = await prisma.stageOutput.upsert({
      where: {
        runId_stageNumber: {
          runId,
          stageNumber
        }
      },
      update: {
        status: status as RunStatus,
        output: output || '',
        completedAt: completedAt ? new Date(completedAt) : (status === 'COMPLETED' ? new Date() : null)
      },
      create: {
        runId,
        stageNumber,
        stageName,
        status: status as RunStatus,
        output: output || '',
        completedAt: completedAt ? new Date(completedAt) : (status === 'COMPLETED' ? new Date() : null)
      }
    })

    console.log(`[StageUpdate] Stage ${stageNumber} updated: ${stageOutput.id}`)

    // 6. If stage 5 is completed, update PipelineRun status to COMPLETED
    if (stageNumber === 5 && status === 'COMPLETED') {
      await prisma.pipelineRun.update({
        where: { id: runId },
        data: {
          status: 'COMPLETED',
          completedAt: new Date()
        }
      })
      console.log(`[StageUpdate] Pipeline ${runId} marked as COMPLETED`)
    }

    // 7. If any stage fails, update PipelineRun status to FAILED
    if (status === 'FAILED') {
      await prisma.pipelineRun.update({
        where: { id: runId },
        data: {
          status: 'FAILED',
          completedAt: new Date()
        }
      })
      console.log(`[StageUpdate] Pipeline ${runId} marked as FAILED`)
    }

    return NextResponse.json({
      success: true,
      stageOutput: {
        id: stageOutput.id,
        stageNumber: stageOutput.stageNumber,
        status: stageOutput.status
      }
    })

  } catch (error) {
    console.error('[StageUpdate] Error processing stage update:', error)

    if (error instanceof Error) {
      console.error('[StageUpdate] Error details:', error.message)
      console.error('[StageUpdate] Error stack:', error.stack)
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

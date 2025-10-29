import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { RunStatus } from '@prisma/client'
import { stageUpdateSchema } from '@/lib/validations/webhook'

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

    // 3. Validate payload using Zod schema
    const validationResult = stageUpdateSchema.safeParse(body)
    if (!validationResult.success) {
      console.error('[StageUpdate] Validation failed:', validationResult.error.format())
      return NextResponse.json(
        {
          error: 'Invalid payload',
          details: validationResult.error.format()
        },
        { status: 400 }
      )
    }

    const { stageNumber, stageName, status, output, completedAt } = validationResult.data

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

    // 6. ALSO save to PipelineRun JSON fields for faster status queries (non-blocking)
    // Stage 5 does NOT have a JSON field (it produces opportunityCards directly)
    const stageOutputMap: Record<number, string> = {
      1: 'stage1Output',
      2: 'stage2Output',
      3: 'stage3Output',
      4: 'stage4Output'
    }

    if (stageNumber <= 4 && output && status === 'COMPLETED') {
      try {
        const columnName = stageOutputMap[stageNumber]

        // Parse output if it's a JSON string
        let outputData: unknown
        try {
          outputData = JSON.parse(output)
        } catch {
          // If parsing fails, treat as plain string
          outputData = output
        }

        await prisma.pipelineRun.update({
          where: { id: runId },
          data: { [columnName]: outputData }
        })

        console.log(`[StageUpdate] Saved stage ${stageNumber} output to ${columnName}`)
      } catch (jsonError) {
        console.error(`[StageUpdate] Failed to save to JSON field (non-critical):`, jsonError)
        // Don't fail the webhook - StageOutput table already has the data
      }
    }

    // 7. NOTE: Do NOT mark PipelineRun as COMPLETED here when stage 5 completes
    //    The /complete webhook will handle final status update AND save opportunities
    //    Marking as COMPLETED here creates a race condition where /complete sees
    //    status=COMPLETED and skips saving opportunities (idempotent check)

    // 8. If any stage fails, update PipelineRun status to FAILED
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

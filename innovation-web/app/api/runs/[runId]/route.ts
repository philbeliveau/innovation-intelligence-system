import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'

/**
 * GET /api/runs/[runId] - Get specific run details with all relations
 */
export async function GET(
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

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { clerkId: userId },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Fetch run with all relations (with limits for performance)
    const run = await prisma.pipelineRun.findFirst({
      where: { id: runId, userId: user.id },
      include: {
        opportunityCards: {
          orderBy: { number: 'asc' },
          take: 100, // Limit to 100 cards (prevents memory issues with large runs)
        },
        inspirationReport: true,
        stageOutputs: {
          orderBy: { stageNumber: 'asc' },
          take: 10, // All stages should fit in 10, but add safety limit
        },
      },
    })

    if (!run) {
      return NextResponse.json(
        { error: 'Run not found' },
        { status: 404 }
      )
    }

    // Transform to API response format
    const response = {
      id: run.id,
      documentName: run.documentName,
      documentUrl: run.documentUrl,
      companyName: run.companyName,
      status: run.status,
      createdAt: run.createdAt.toISOString(),
      completedAt: run.completedAt?.toISOString() || null,
      duration: run.duration,
      pipelineVersion: run.pipelineVersion,
      opportunityCards: run.opportunityCards.map((card) => ({
        id: card.id,
        number: card.number,
        title: card.title,
        content: card.content,
        isStarred: card.isStarred,
      })),
      inspirationReport: run.inspirationReport
        ? {
            selectedTrack: run.inspirationReport.selectedTrack,
            nonSelectedTrack: run.inspirationReport.nonSelectedTrack,
            stage1Output: run.inspirationReport.stage1Output,
            stage2Output: run.inspirationReport.stage2Output,
            stage3Output: run.inspirationReport.stage3Output,
            stage4Output: run.inspirationReport.stage4Output,
            stage5Output: run.inspirationReport.stage5Output,
          }
        : null,
      stageOutputs: run.stageOutputs.map((stage) => ({
        stageNumber: stage.stageNumber,
        stageName: stage.stageName,
        status: stage.status,
        output: stage.output,
        completedAt: stage.completedAt?.toISOString() || null,
      })),
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('[API /runs/[runId]] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/runs/[runId] - Delete run and all related data (cascade)
 */
export async function DELETE(
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

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { clerkId: userId },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Verify run ownership and delete (cascade will remove related records)
    const run = await prisma.pipelineRun.findFirst({
      where: { id: runId, userId: user.id },
    })

    if (!run) {
      return NextResponse.json(
        { error: 'Run not found' },
        { status: 404 }
      )
    }

    // Delete run (cascade delete handles opportunityCards, inspirationReport, stageOutputs)
    await prisma.pipelineRun.delete({
      where: { id: runId },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('[API /runs/[runId]] Delete error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

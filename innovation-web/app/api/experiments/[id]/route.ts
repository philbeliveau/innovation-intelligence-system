import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * GET /api/experiments/[id] - Get a single experiment by ID
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const experimentId = params.id

    const experiment = await prisma.experiment.findUnique({
      where: { id: experimentId },
    })

    if (!experiment) {
      return NextResponse.json(
        { error: `Experiment ${experimentId} not found` },
        { status: 404 }
      )
    }

    return NextResponse.json(experiment, { status: 200 })

  } catch (error) {
    console.error('[API /experiments/[id] GET] Error:', error)
    return NextResponse.json(
      { error: 'Failed to retrieve experiment', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/experiments/[id] - Delete an experiment
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const experimentId = params.id

    // Check if experiment exists
    const existing = await prisma.experiment.findUnique({
      where: { id: experimentId },
    })

    if (!existing) {
      return NextResponse.json(
        { error: `Experiment ${experimentId} not found` },
        { status: 404 }
      )
    }

    // Delete experiment
    await prisma.experiment.delete({
      where: { id: experimentId },
    })

    return NextResponse.json(
      {
        success: true,
        message: 'Experiment deleted successfully',
        experimentId,
      },
      { status: 200 }
    )

  } catch (error) {
    console.error('[API /experiments/[id] DELETE] Error:', error)
    return NextResponse.json(
      { error: 'Failed to delete experiment', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

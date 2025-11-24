import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * PUT /api/experiments/[id]/rename - Rename an experiment
 *
 * Request body:
 * {
 *   newName: string (1-200 characters)
 * }
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const experimentId = params.id
    const body = await request.json()

    // Validate newName
    const { newName } = body
    if (!newName || typeof newName !== 'string' || newName.length < 1 || newName.length > 200) {
      return NextResponse.json(
        { error: 'Invalid newName. Must be a string between 1-200 characters.' },
        { status: 400 }
      )
    }

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

    // Update experimentNotes with custom name prefix
    // Format: "[NAME: {newName}] {existingNotes}"
    const currentNotes = existing.experimentNotes || ''

    // Remove existing [NAME: ...] prefix if present
    const notesWithoutPrefix = currentNotes.replace(/^\[NAME: .*?\]\s*/, '')

    // Add new name prefix
    const updatedNotes = `[NAME: ${newName}] ${notesWithoutPrefix}`.trim()

    // Update experiment
    await prisma.experiment.update({
      where: { id: experimentId },
      data: { experimentNotes: updatedNotes },
    })

    return NextResponse.json(
      {
        success: true,
        message: `Experiment renamed to '${newName}'`,
        experimentId,
      },
      { status: 200 }
    )

  } catch (error) {
    console.error('[API /experiments/[id]/rename PUT] Error:', error)
    return NextResponse.json(
      { error: 'Failed to rename experiment', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

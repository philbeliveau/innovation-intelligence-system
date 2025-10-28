/**
 * GET /api/pipeline/[runId]/download/all
 *
 * Download all opportunity cards as a ZIP file containing markdown files
 */

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { auth } from '@clerk/nextjs/server'
import JSZip from 'jszip'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }

    const { runId } = await params

    // Fetch run with opportunity cards
    const run = await prisma.pipelineRun.findUnique({
      where: {
        id: runId,
        user: {
          clerkId: userId,
        },
      },
      include: {
        opportunityCards: {
          orderBy: {
            number: 'asc',
          },
        },
      },
    })

    if (!run) {
      return NextResponse.json({ error: 'Run not found' }, { status: 404 })
    }

    if (!run.opportunityCards || run.opportunityCards.length === 0) {
      return NextResponse.json(
        { error: 'No opportunity cards found for this run' },
        { status: 404 }
      )
    }

    // Create ZIP file with JSZip
    const zip = new JSZip()

    // Add each opportunity card as markdown file
    run.opportunityCards.forEach((card: { number: number; title: string; content: string }) => {
      const fileName = `spark-${card.number}-${card.title.replace(/[^a-z0-9]/gi, '-').toLowerCase()}.md`
      const content = `# ${card.title}\n\n${card.content}`
      zip.file(fileName, content)
    })

    // Generate ZIP buffer
    const zipBuffer = await zip.generateAsync({ type: 'uint8array' })

    // Return ZIP file
    return new NextResponse(Buffer.from(zipBuffer), {
      headers: {
        'Content-Type': 'application/zip',
        'Content-Disposition': `attachment; filename="sparks-${runId}.zip"`,
      },
    })
  } catch (error) {
    console.error('Download all error:', error)
    return NextResponse.json(
      { error: 'Failed to generate download' },
      { status: 500 }
    )
  }
}

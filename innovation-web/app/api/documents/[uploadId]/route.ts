import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'

/**
 * GET /api/documents/:uploadId
 *
 * Retrieves document metadata from database by uploadId.
 * Enables persistent access to uploaded documents across sessions.
 *
 * Response:
 * - blobUrl: Vercel Blob URL to PDF
 * - fileName: Original filename
 * - fileSize: File size in bytes
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ uploadId: string }> }
) {
  try {
    // Check authentication
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      )
    }

    // Get uploadId from params
    const { uploadId } = await params

    // Extract timestamp from uploadId (format: "upload-1234567890")
    const timestampMatch = uploadId.match(/upload-(\d+)/)
    if (!timestampMatch) {
      return NextResponse.json(
        { error: 'Invalid uploadId format' },
        { status: 400 }
      )
    }

    const timestamp = parseInt(timestampMatch[1])
    const uploadDate = new Date(timestamp)

    // Find user in database
    const user = await prisma.user.findUnique({
      where: { clerkId: userId }
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Query Document table for documents uploaded around this timestamp
    // Allow 5-second window to account for processing time
    const fiveSecondsMs = 5000
    const document = await prisma.document.findFirst({
      where: {
        userId: user.id,
        uploadedAt: {
          gte: new Date(uploadDate.getTime() - fiveSecondsMs),
          lte: new Date(uploadDate.getTime() + fiveSecondsMs)
        }
      },
      orderBy: { uploadedAt: 'desc' }
    })

    if (!document) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      )
    }

    // Return document metadata
    return NextResponse.json({
      blobUrl: document.blobUrl,
      fileName: document.fileName,
      fileSize: document.fileSize,
      uploadedAt: document.uploadedAt.toISOString()
    })

  } catch (error) {
    console.error('[GET /api/documents/:uploadId] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { auth } from '@clerk/nextjs/server'
import { runPipeline } from '@/lib/backend-client'
import { prisma } from '@/lib/prisma'

export async function POST(request: NextRequest) {
  try {
    // Check authentication
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      )
    }

    // Parse request body
    const body = await request.json()
    const { blob_url, upload_id } = body

    // Validate required fields
    if (!blob_url || !upload_id) {
      return NextResponse.json(
        { error: 'Missing required fields: blob_url and upload_id' },
        { status: 400 }
      )
    }

    // Read company ID from cookie
    const cookieStore = await cookies()
    const companyId = cookieStore.get('company_id')?.value
    const companyName = cookieStore.get('company_name')?.value

    if (!companyId) {
      return NextResponse.json(
        { error: 'No company selected. Please complete onboarding first.' },
        { status: 401 }
      )
    }

    // Sanitize company_id to prevent command injection
    const sanitizedCompanyId = companyId.replace(/[^a-z0-9-]/gi, '')
    if (sanitizedCompanyId !== companyId) {
      return NextResponse.json(
        { error: 'Invalid company identifier' },
        { status: 400 }
      )
    }

    // Validate blob URL format (basic check)
    if (!blob_url.startsWith('https://') && !blob_url.startsWith('http://')) {
      return NextResponse.json(
        { error: 'Invalid blob URL format' },
        { status: 400 }
      )
    }

    console.log(`[API /run] Triggering pipeline for brand: ${sanitizedCompanyId}, blob: ${blob_url}`)

    // Call Railway backend to run pipeline
    let backendResponse
    try {
      backendResponse = await runPipeline(blob_url, sanitizedCompanyId)
    } catch (error) {
      console.error('[API /run] Backend client error:', error)

      // Network/timeout errors
      if (error instanceof Error) {
        if (error.message.includes('timeout')) {
          return NextResponse.json(
            { error: 'Backend is slow to respond. Please try again.' },
            { status: 504 }
          )
        }

        if (error.message.includes('fetch failed') || error.message.includes('Failed to fetch')) {
          return NextResponse.json(
            { error: 'Cannot connect to backend. Please try again later.' },
            { status: 503 }
          )
        }

        // Backend returned an error
        return NextResponse.json(
          { error: error.message || 'Pipeline failed to start' },
          { status: 500 }
        )
      }

      // Unknown error
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      )
    }

    // Get document name from blob URL
    const documentName = extractDocumentName(blob_url)

    // Create PipelineRun record in database
    try {
      // Find or create Prisma user from Clerk userId
      const user = await prisma.user.upsert({
        where: { clerkId: userId },
        update: {},
        create: {
          clerkId: userId,
          email: `user-${userId}@temp.com`, // Temporary email, can be updated later
        }
      })

      // Create PipelineRun record with Railway run_id
      await prisma.pipelineRun.create({
        data: {
          id: backendResponse.run_id, // Use Railway's run_id as primary key
          userId: user.id,
          documentName,
          documentUrl: blob_url,
          companyName: companyName || sanitizedCompanyId,
          status: 'PROCESSING',
          pipelineVersion: '1.0',
          createdAt: new Date(),
        }
      })

      console.log(`[API /run] Created PipelineRun record: ${backendResponse.run_id}`)
    } catch (dbError) {
      // Log database error but don't fail the pipeline start
      // The pipeline is already running on Railway
      console.error('[API /run] Database persistence error:', dbError)
      // We still return success since the pipeline started
    }

    // Return run_id from Railway backend
    console.log(`[API /run] Pipeline started successfully: ${backendResponse.run_id}`)
    return NextResponse.json({
      run_id: backendResponse.run_id,
      status: backendResponse.status,
    })
  } catch (error) {
    console.error('Unexpected error in /api/run:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * Extract document name from Vercel Blob URL
 * @param blobUrl - Full Vercel Blob URL
 * @returns Document name without timestamp prefix
 */
function extractDocumentName(blobUrl: string): string {
  try {
    // Extract filename from URL: https://xxx.blob.vercel-storage.com/uploads/1234567890-filename.pdf
    const url = new URL(blobUrl)
    const pathname = url.pathname
    const filename = pathname.split('/').pop() || 'document.pdf'

    // Remove timestamp prefix (format: 1234567890-filename.pdf → filename.pdf)
    const withoutTimestamp = filename.replace(/^\d+-/, '')

    // Decode URL encoding and sanitize
    return decodeURIComponent(withoutTimestamp)
  } catch {
    return 'document.pdf'
  }
}

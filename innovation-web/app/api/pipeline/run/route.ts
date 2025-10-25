import { NextRequest, NextResponse } from 'next/server'
import { cookies } from 'next/headers'
import { auth } from '@clerk/nextjs/server'
import { runPipeline } from '@/lib/backend-client'
import { prisma } from '@/lib/prisma'

/**
 * POST /api/pipeline/run
 *
 * Starts a new pipeline execution for a given document and brand.
 *
 * Request body:
 * - blob_url: Vercel Blob URL to PDF document
 * - upload_id: Upload record ID (optional, for tracking)
 *
 * Response:
 * - run_id: Unique pipeline run identifier
 * - status: 'running'
 */
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

    console.log(`[API /pipeline/run] Triggering pipeline for brand: ${sanitizedCompanyId}, blob: ${blob_url}`)

    // Get document name from blob URL
    const documentName = extractDocumentName(blob_url)

    // Generate run_id BEFORE calling backend (to avoid race condition)
    // Backend will use this same run_id when calling webhooks
    const timestamp = Date.now()
    const randomSuffix = Math.floor(Math.random() * 10000)
    const runId = `run-${timestamp}-${randomSuffix}`

    // Create PipelineRun record BEFORE calling backend
    // This prevents 404 errors when backend immediately calls stage-update webhook
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

      // Create PipelineRun record with pre-generated run_id
      await prisma.pipelineRun.create({
        data: {
          id: runId,
          userId: user.id,
          documentName,
          documentUrl: blob_url,
          companyName: companyName || sanitizedCompanyId,
          status: 'PROCESSING',
          pipelineVersion: '1.0',
          createdAt: new Date(),
        }
      })

      console.log(`[API /pipeline/run] Created PipelineRun record: ${runId}`)
    } catch (dbError) {
      console.error('[API /pipeline/run] Database persistence error:', dbError)
      return NextResponse.json(
        { error: 'Failed to create pipeline run record' },
        { status: 500 }
      )
    }

    // Now call Railway backend with pre-generated run_id
    let backendResponse
    try {
      backendResponse = await runPipeline(blob_url, sanitizedCompanyId, runId)
    } catch (error) {
      console.error('[API /pipeline/run] Backend client error:', error)

      // Mark pipeline as failed in database
      await prisma.pipelineRun.update({
        where: { id: runId },
        data: { status: 'FAILED', completedAt: new Date() }
      }).catch(() => {}) // Ignore DB errors here

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

    // Return run_id to frontend
    console.log(`[API /pipeline/run] Pipeline started successfully: ${runId}`)
    return NextResponse.json({
      run_id: runId,
      status: backendResponse.status,
    })
  } catch (error) {
    console.error('Unexpected error in /api/pipeline/run:', error)
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

import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

/**
 * POST /api/pipeline/init
 *
 * Initialize PipelineRun record when backend is called directly (e.g., via MCP).
 * This endpoint is called by the backend when it generates its own run_id.
 *
 * Authentication: X-Webhook-Secret header (same as other webhooks)
 *
 * Request body:
 * {
 *   runId: string,
 *   blobUrl: string,
 *   brandName: string,
 *   documentName: string
 * }
 */
export async function POST(request: NextRequest) {
  try {
    // 1. Authenticate webhook using shared secret
    const webhookSecret = request.headers.get('X-Webhook-Secret')
    const expectedSecret = process.env.WEBHOOK_SECRET

    if (!expectedSecret) {
      console.error('[PipelineInit] WEBHOOK_SECRET environment variable is not set')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    if (webhookSecret !== expectedSecret) {
      console.error('[PipelineInit] Authentication failed: Invalid secret')
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    // 2. Parse request body
    const body = await request.json()
    const { runId, blobUrl, brandName, documentName } = body

    // 3. Validate required fields
    if (!runId || !blobUrl || !brandName) {
      return NextResponse.json(
        { error: 'Missing required fields: runId, blobUrl, brandName' },
        { status: 400 }
      )
    }

    console.log(`[PipelineInit] Initializing run: ${runId} for ${brandName}`)

    // 4. Check if run already exists
    const existingRun = await prisma.pipelineRun.findUnique({
      where: { id: runId }
    })

    if (existingRun) {
      console.log(`[PipelineInit] Run ${runId} already exists - skipping creation`)
      return NextResponse.json({
        success: true,
        message: 'Run already exists',
        runId: existingRun.id
      })
    }

    // 5. Create system user for backend-initiated runs (if not exists)
    const systemUser = await prisma.user.upsert({
      where: { clerkId: 'system-backend' },
      update: {},
      create: {
        clerkId: 'system-backend',
        email: 'backend@system.local'
      }
    })

    // 6. Create PipelineRun record
    const pipelineRun = await prisma.pipelineRun.create({
      data: {
        id: runId,
        userId: systemUser.id,
        documentName: documentName || 'document.pdf',
        documentUrl: blobUrl,
        companyName: brandName,
        status: 'PROCESSING',
        pipelineVersion: '1.0',
        createdAt: new Date()
      }
    })

    console.log(`[PipelineInit] Created PipelineRun record: ${pipelineRun.id}`)

    return NextResponse.json({
      success: true,
      runId: pipelineRun.id,
      status: pipelineRun.status
    })

  } catch (error) {
    console.error('[PipelineInit] Error initializing pipeline run:', error)

    if (error instanceof Error) {
      console.error('[PipelineInit] Error details:', error.message)
      console.error('[PipelineInit] Error stack:', error.stack)
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

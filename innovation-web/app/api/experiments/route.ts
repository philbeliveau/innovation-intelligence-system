import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import { QualityTag } from '@prisma/client'

export type { QualityTag }

/**
 * POST /api/experiments - Save a complete pipeline experiment
 *
 * Request body:
 * {
 *   runId: string
 *   reportText?: string
 *   reportName?: string
 *   brandProfile: object (JSONB)
 *   stageOutputs: object (JSONB)
 *   qualityTag?: "good" | "needs_work" | "failed"
 *   experimentNotes?: string
 *   executionTimeSeconds?: number
 *   tokenUsage?: object (JSONB)
 *   costUsd?: number
 *   pipelineVersion?: string
 * }
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Validate required fields
    const { runId, brandProfile, stageOutputs } = body

    if (!runId || !brandProfile || !stageOutputs) {
      return NextResponse.json(
        {
          error: 'Missing required fields: runId, brandProfile, stageOutputs',
          received: { runId: !!runId, brandProfile: !!brandProfile, stageOutputs: !!stageOutputs }
        },
        { status: 400 }
      )
    }

    // Validate qualityTag if provided
    const validQualityTags = ['good', 'needs_work', 'failed']
    if (body.qualityTag && !validQualityTags.includes(body.qualityTag)) {
      return NextResponse.json(
        { error: `Invalid qualityTag. Must be one of: ${validQualityTags.join(', ')}` },
        { status: 400 }
      )
    }

    // Create experiment record
    const experiment = await prisma.experiment.create({
      data: {
        runId: body.runId,
        reportText: body.reportText || null,
        reportName: body.reportName || null,
        brandProfile: body.brandProfile,
        stageOutputs: body.stageOutputs,
        qualityTag: body.qualityTag || null,
        experimentNotes: body.experimentNotes || null,
        executionTimeSeconds: body.executionTimeSeconds || null,
        tokenUsage: body.tokenUsage || null,
        costUsd: body.costUsd || null,
        pipelineVersion: body.pipelineVersion || '1.0',
      },
    })

    return NextResponse.json({
      success: true,
      experimentId: experiment.id,
      runId: experiment.runId,
    }, { status: 201 })

  } catch (error) {
    console.error('[API /experiments POST] Error:', error)

    // Handle unique constraint violation (duplicate run_id)
    if (error instanceof Error && error.message.includes('Unique constraint')) {
      return NextResponse.json(
        { error: 'Experiment with this run_id already exists' },
        { status: 409 }
      )
    }

    return NextResponse.json(
      { error: 'Failed to save experiment', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

/**
 * GET /api/experiments - Retrieve experiments with filtering and pagination
 *
 * Query params:
 * - page: Page number (default: 1)
 * - pageSize: Number of experiments per page (default: 20, max: 100)
 * - qualityTag: Filter by quality tag (good | needs_work | failed)
 * - brandName: Filter by brand name (searches brandProfile JSON)
 * - startDate: Filter by timestamp >= startDate (ISO format)
 * - endDate: Filter by timestamp <= endDate (ISO format)
 * - pipelineVersion: Filter by pipeline version
 * - orderBy: Sort field (timestamp_desc | timestamp_asc | cost_desc) default: timestamp_desc
 */
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams

    // Parse pagination params
    const page = parseInt(searchParams.get('page') || '1', 10)
    const pageSize = Math.min(
      parseInt(searchParams.get('pageSize') || '20', 10),
      100 // Max 100 per page
    )

    // Validate pagination
    if (page < 1 || pageSize < 1) {
      return NextResponse.json(
        { error: 'Invalid pagination parameters' },
        { status: 400 }
      )
    }

    // Parse filters
    const qualityTag = searchParams.get('qualityTag') || null
    const brandName = searchParams.get('brandName') || null
    const startDate = searchParams.get('startDate') || null
    const endDate = searchParams.get('endDate') || null
    const pipelineVersion = searchParams.get('pipelineVersion') || null
    const orderBy = searchParams.get('orderBy') || 'timestamp_desc'

    // Build where clause
    const where: any = {}

    if (qualityTag) {
      where.qualityTag = qualityTag
    }

    if (pipelineVersion) {
      where.pipelineVersion = pipelineVersion
    }

    // Date range filter
    if (startDate || endDate) {
      where.timestamp = {}
      if (startDate) {
        where.timestamp.gte = new Date(startDate)
      }
      if (endDate) {
        where.timestamp.lte = new Date(endDate)
      }
    }

    // Brand name filter (JSONB query)
    // Note: Prisma doesn't support JSONB path queries directly in findMany
    // We'll fetch all matching records and filter in-memory
    // For production, consider using raw SQL for better performance

    // Determine sort order
    let orderByClause: any = { timestamp: 'desc' }
    switch (orderBy) {
      case 'timestamp_asc':
        orderByClause = { timestamp: 'asc' }
        break
      case 'cost_desc':
        orderByClause = { costUsd: 'desc' }
        break
      case 'timestamp_desc':
      default:
        orderByClause = { timestamp: 'desc' }
    }

    // Fetch experiments
    let experiments = await prisma.experiment.findMany({
      where,
      orderBy: orderByClause,
      skip: (page - 1) * pageSize,
      take: pageSize,
    })

    // Post-filter by brand name if provided (JSONB filtering)
    if (brandName) {
      experiments = experiments.filter((exp: any) => {
        const profile = exp.brandProfile as any
        return profile?.brand_name === brandName
      })
    }

    // Get total count (without pagination)
    let total = await prisma.experiment.count({ where })

    // Adjust total if brand name filter was applied
    if (brandName) {
      const allExperiments = await prisma.experiment.findMany({ where })
      total = allExperiments.filter((exp: any) => {
        const profile = exp.brandProfile as any
        return profile?.brand_name === brandName
      }).length
    }

    return NextResponse.json({
      experiments,
      pagination: {
        page,
        pageSize,
        total,
        totalPages: Math.ceil(total / pageSize),
      },
      filters: {
        qualityTag,
        brandName,
        startDate,
        endDate,
        pipelineVersion,
        orderBy,
      },
    })

  } catch (error) {
    console.error('[API /experiments GET] Error:', error)
    return NextResponse.json(
      { error: 'Failed to retrieve experiments', details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    )
  }
}

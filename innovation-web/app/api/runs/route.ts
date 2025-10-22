import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'
import { RunStatus } from '@prisma/client'

export type { RunStatus }

export interface SidebarRun {
  id: string
  documentName: string
  companyName: string
  createdAt: string
  status: RunStatus
  cardCount: number
}

interface RunsResponse {
  runs: SidebarRun[]
  total: number
  page: number
  pageSize: number
  uniqueCompanies: string[]
}

/**
 * GET /api/runs - Fetch user's pipeline runs with pagination, filtering, and sorting
 *
 * Query params:
 * - page: Page number (default: 1)
 * - pageSize: Number of runs per page (default: 12)
 * - companyId: Filter by company name
 * - status: Filter by status (PROCESSING | COMPLETED | FAILED | CANCELLED)
 * - dateRange: Filter by date (today | week | month | all)
 * - search: Search by document name (case-insensitive)
 * - sort: Sort order (newest | oldest | company-az)
 */
export async function GET(request: NextRequest) {
  try {
    // Check authentication
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      )
    }

    // Parse query parameters
    const searchParams = request.nextUrl.searchParams
    const page = parseInt(searchParams.get('page') || '1', 10)
    const pageSize = parseInt(searchParams.get('pageSize') || '12', 10)
    const companyFilter = searchParams.get('companyId') || null
    const statusFilter = searchParams.get('status') as RunStatus | null
    const dateRangeFilter = searchParams.get('dateRange') || 'all'
    const searchQuery = searchParams.get('search')?.toLowerCase() || null
    const sortOption = searchParams.get('sort') || 'newest'

    // Validate pagination params
    if (page < 1 || pageSize < 1 || pageSize > 100) {
      return NextResponse.json(
        { error: 'Invalid pagination parameters' },
        { status: 400 }
      )
    }

    // Get or create user in database
    let user = await prisma.user.findUnique({
      where: { clerkId: userId },
    })

    if (!user) {
      // Auto-create user on first API call
      const authSession = await auth()
      user = await prisma.user.create({
        data: {
          clerkId: userId,
          email: (authSession as { emailAddresses?: Array<{ emailAddress: string }> })?.emailAddresses?.[0]?.emailAddress || `user-${userId}@temp.com`,
          name: null,
        },
      })
    }

    // Build Prisma where clause for filters
    const where: Record<string, unknown> = { userId: user.id }

    if (companyFilter) {
      where.companyName = companyFilter
    }

    if (statusFilter) {
      where.status = statusFilter
    }

    if (searchQuery) {
      where.documentName = {
        contains: searchQuery,
        mode: 'insensitive',
      }
    }

    // Apply date range filter
    if (dateRangeFilter !== 'all') {
      const now = new Date()
      const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const startOfWeek = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)

      let cutoffDate: Date
      switch (dateRangeFilter) {
        case 'today':
          cutoffDate = startOfToday
          break
        case 'week':
          cutoffDate = startOfWeek
          break
        case 'month':
          cutoffDate = startOfMonth
          break
        default:
          cutoffDate = new Date(0)
      }

      where.createdAt = { gte: cutoffDate }
    }

    // Determine sort order for Prisma
    let orderBy: Record<string, string> = { createdAt: 'desc' }
    switch (sortOption) {
      case 'oldest':
        orderBy = { createdAt: 'asc' }
        break
      case 'company-az':
        orderBy = { companyName: 'asc' }
        break
      case 'newest':
      default:
        orderBy = { createdAt: 'desc' }
    }

    // Fetch runs from database with card count
    const dbRuns = await prisma.pipelineRun.findMany({
      where,
      orderBy,
      skip: (page - 1) * pageSize,
      take: pageSize,
      include: {
        _count: {
          select: { opportunityCards: true },
        },
      },
    })

    // Get total count for pagination
    const total = await prisma.pipelineRun.count({ where })

    // Transform to API response format
    const runs: SidebarRun[] = dbRuns.map((run) => ({
      id: run.id,
      documentName: run.documentName,
      companyName: run.companyName,
      createdAt: run.createdAt.toISOString(),
      status: run.status,
      cardCount: run._count.opportunityCards,
    }))

    // Get unique companies for filter dropdown (query all companies for this user)
    const allCompanies = await prisma.pipelineRun.findMany({
      where: { userId: user.id },
      select: { companyName: true },
      distinct: ['companyName'],
      orderBy: { companyName: 'asc' },
    })
    const uniqueCompanies = allCompanies.map((r) => r.companyName)

    const response: RunsResponse = {
      runs,
      total,
      page,
      pageSize,
      uniqueCompanies,
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('[API /runs] Unexpected error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

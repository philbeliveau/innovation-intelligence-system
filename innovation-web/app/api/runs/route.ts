import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { list } from '@vercel/blob'

export type RunStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'

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

    // Fetch blobs from Vercel Blob storage with user ID prefix
    const { blobs } = await list({
      prefix: `${userId}/`,
      limit: 1000, // Fetch all user blobs (adjust if needed)
    })

    // Parse metadata from blob names and filter for valid runs
    // Expected format: {userId}/{uploadId}_{filename}
    let runs = blobs
      .map(blob => {
        try {
          // Extract upload ID and filename from pathname
          const pathParts = blob.pathname.split('/')
          if (pathParts.length < 2) return null

          const fileName = pathParts[pathParts.length - 1]
          const uploadId = fileName.split('_')[0]

          // Extract metadata from blob (stored during upload)
          // For now, we'll derive status and cardCount from naming conventions
          // In production, this should come from a database

          // Determine status based on blob metadata or naming
          // This is a placeholder - real implementation needs database
          const status: RunStatus = 'COMPLETED'
          const cardCount = 5 // Placeholder

          // Extract document name (remove upload ID prefix)
          const documentName = fileName.substring(fileName.indexOf('_') + 1)

          // Get company name from metadata if available
          const companyName = blob.downloadUrl.includes('lactalis') ? 'Lactalis Canada' : 'Unknown Company'

          return {
            id: uploadId,
            documentName,
            companyName,
            createdAt: blob.uploadedAt.toISOString(),
            status,
            cardCount,
          }
        } catch (error) {
          console.error('[API /runs] Failed to parse blob metadata:', error)
          return null
        }
      })
      .filter((run) => run !== null) as SidebarRun[]

    // Apply filters
    if (companyFilter) {
      runs = runs.filter(run => run.companyName === companyFilter)
    }

    if (statusFilter) {
      runs = runs.filter(run => run.status === statusFilter)
    }

    if (searchQuery) {
      runs = runs.filter(run => run.documentName.toLowerCase().includes(searchQuery))
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
          cutoffDate = new Date(0) // Beginning of time
      }

      runs = runs.filter(run => new Date(run.createdAt) >= cutoffDate)
    }

    // Apply sorting
    runs.sort((a, b) => {
      switch (sortOption) {
        case 'oldest':
          return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        case 'company-az':
          return a.companyName.localeCompare(b.companyName)
        case 'newest':
        default:
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      }
    })

    // Get unique companies for filter dropdown
    const uniqueCompanies = Array.from(new Set(runs.map(run => run.companyName))).sort()

    // Apply pagination
    const startIndex = (page - 1) * pageSize
    const endIndex = startIndex + pageSize
    const paginatedRuns = runs.slice(startIndex, endIndex)

    const response: RunsResponse = {
      runs: paginatedRuns,
      total: runs.length,
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

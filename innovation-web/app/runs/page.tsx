'use client'

import { useState, useEffect, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import RunCard from '@/components/RunCard'
import { SidebarRun } from '@/app/api/runs/route'
import { Search, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert'

type RunStatus = 'all' | 'COMPLETED' | 'PROCESSING' | 'FAILED' | 'CANCELLED'
type DateRange = 'all' | 'today' | 'week' | 'month'
type SortOption = 'newest' | 'oldest' | 'company-az'

interface RunsResponse {
  runs: SidebarRun[]
  total: number
  page: number
  pageSize: number
  uniqueCompanies: string[]
}

function RunsPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  // State
  const [runs, setRuns] = useState<SidebarRun[]>([])
  const [uniqueCompanies, setUniqueCompanies] = useState<string[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCompany, setSelectedCompany] = useState<string>('all')
  const [selectedStatus, setSelectedStatus] = useState<RunStatus>('all')
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>('all')
  const [sortOption, setSortOption] = useState<SortOption>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('runs-sort-preference') as SortOption) || 'newest'
    }
    return 'newest'
  })

  // Pagination state
  const pageSize = 12
  const currentPage = parseInt(searchParams.get('page') || '1', 10)
  const totalPages = Math.ceil(total / pageSize)

  // Fetch runs with filters
  const fetchRuns = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const params = new URLSearchParams({
        page: currentPage.toString(),
        pageSize: pageSize.toString(),
      })

      if (selectedCompany !== 'all') params.append('companyId', selectedCompany)
      if (selectedStatus !== 'all') params.append('status', selectedStatus)
      if (selectedDateRange !== 'all') params.append('dateRange', selectedDateRange)
      if (searchQuery) params.append('search', searchQuery)
      if (sortOption !== 'newest') params.append('sort', sortOption)

      const response = await fetch(`/api/runs?${params.toString()}`)

      if (!response.ok) {
        throw new Error('Failed to fetch runs')
      }

      const data: RunsResponse = await response.json()
      setRuns(data.runs)
      setTotal(data.total)
      if (data.uniqueCompanies) {
        setUniqueCompanies(data.uniqueCompanies)
      }
    } catch (err) {
      console.error('Error fetching runs:', err)
      setError(err instanceof Error ? err.message : 'Failed to load runs')
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch on mount and when filters change
  useEffect(() => {
    fetchRuns()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, selectedCompany, selectedStatus, selectedDateRange, searchQuery, sortOption])

  // Save sort preference
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('runs-sort-preference', sortOption)
    }
  }, [sortOption])

  // Handle page navigation
  const goToPage = (page: number) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('page', page.toString())
    router.push(`/runs?${params.toString()}`)
  }

  // Handle delete
  const handleDelete = (id: string) => {
    setRuns(prev => prev.filter(run => run.id !== id))
    setTotal(prev => prev - 1)
  }

  // Handle rerun
  const handleRerun = () => {
    // Refresh the list to show the new run
    fetchRuns()
  }

  // Calculate unique company count
  const companyCount = uniqueCompanies.length

  return (
    <div className="min-h-screen bg-white p-6 lg:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-black">Your Innovation Runs</h1>
          <p className="text-gray-600">
            {total} total runs · {companyCount} {companyCount === 1 ? 'company' : 'companies'}
          </p>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 p-6 border-4 border-black bg-gray-50">
          {/* Search */}
          <div className="lg:col-span-2 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              placeholder="Search by document name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 border-2 border-black"
            />
          </div>

          {/* Company Filter */}
          <Select value={selectedCompany} onValueChange={setSelectedCompany}>
            <SelectTrigger className="border-2 border-black">
              <SelectValue placeholder="All Companies" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Companies</SelectItem>
              {uniqueCompanies.map(company => (
                <SelectItem key={company} value={company}>
                  {company}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {/* Status Filter */}
          <Select value={selectedStatus} onValueChange={(value) => setSelectedStatus(value as RunStatus)}>
            <SelectTrigger className="border-2 border-black">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="PROCESSING">Processing</SelectItem>
              <SelectItem value="FAILED">Failed</SelectItem>
            </SelectContent>
          </Select>

          {/* Date Range Filter */}
          <Select value={selectedDateRange} onValueChange={(value) => setSelectedDateRange(value as DateRange)}>
            <SelectTrigger className="border-2 border-black">
              <SelectValue placeholder="All Time" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
              <SelectItem value="month">This Month</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sort Controls */}
        <div className="flex justify-between items-center">
          <Select value={sortOption} onValueChange={(value) => setSortOption(value as SortOption)}>
            <SelectTrigger className="w-48 border-2 border-black">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="oldest">Oldest First</SelectItem>
              <SelectItem value="company-az">Company A-Z</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Error State */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchRuns}
                className="ml-4"
              >
                Retry
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Loading Skeletons */}
        {isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="border-4 border-black p-6 space-y-4">
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-8 w-1/2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
                <div className="flex gap-2 pt-2">
                  <Skeleton className="h-9 flex-1" />
                  <Skeleton className="h-9 flex-1" />
                  <Skeleton className="h-9 w-9" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && runs.length === 0 && !error && (
          <div className="text-center py-20 border-4 border-black">
            <h2 className="text-2xl font-bold mb-2">No runs yet</h2>
            <p className="text-gray-600 mb-6">Upload a document to get started.</p>
            <Button
              onClick={() => router.push('/upload')}
              className="bg-black text-white hover:bg-gray-800 border-2 border-black"
            >
              Upload Document
            </Button>
          </div>
        )}

        {/* Run Cards Grid */}
        {!isLoading && runs.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {runs.map(run => (
                <RunCard
                  key={run.id}
                  run={run}
                  onDelete={handleDelete}
                  onRerun={handleRerun}
                />
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-8">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="border-2 border-black"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>

                <div className="flex gap-1">
                  {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                    let pageNum: number
                    if (totalPages <= 5) {
                      pageNum = i + 1
                    } else if (currentPage <= 3) {
                      pageNum = i + 1
                    } else if (currentPage >= totalPages - 2) {
                      pageNum = totalPages - 4 + i
                    } else {
                      pageNum = currentPage - 2 + i
                    }

                    return (
                      <Button
                        key={pageNum}
                        variant={currentPage === pageNum ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => goToPage(pageNum)}
                        className={
                          currentPage === pageNum
                            ? 'bg-black text-white border-2 border-black'
                            : 'border-2 border-black'
                        }
                      >
                        {pageNum}
                      </Button>
                    )
                  })}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="border-2 border-black"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default function RunsPage() {
  return (
    <Suspense fallback={
      <div className="container mx-auto px-6 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">All Runs</h1>
            <p className="text-gray-600">Loading runs...</p>
          </div>
        </div>
      </div>
    }>
      <RunsPageContent />
    </Suspense>
  )
}

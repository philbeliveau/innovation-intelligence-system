'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
  BreadcrumbPage,
} from '@/components/ui/breadcrumb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Play, Download, Trash2, AlertCircle } from 'lucide-react'
import RunDetailOpportunityCards from '@/components/RunDetailOpportunityCards'
import RunDetailFullReport from '@/components/RunDetailFullReport'
import RunDetailPipelineStages from '@/components/RunDetailPipelineStages'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { toast } from 'sonner'

interface OpportunityCard {
  id: string
  number: number
  title: string
  content: string
  isStarred: boolean
}

interface InspirationReport {
  id: string
  selectedTrack: string
  nonSelectedTrack: string
  stage1Output: string
  stage2Output: string
  stage3Output: string
  stage4Output: string
  stage5Output: string
}

interface StageOutput {
  id: string
  stageNumber: number
  stageName: string
  status: 'COMPLETED' | 'FAILED' | 'PROCESSING'
  output: string
  completedAt: string | null
}

interface RunDetail {
  id: string
  documentName: string
  companyName: string
  status: 'COMPLETED' | 'PROCESSING' | 'FAILED' | 'CANCELLED'
  createdAt: string
  completedAt: string | null
  duration: number | null
  pipelineVersion: string
  opportunityCards: OpportunityCard[]
  inspirationReport: InspirationReport | null
  stageOutputs: StageOutput[]
}

export default function RunDetailPage({ params }: { params: Promise<{ runId: string }> }) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [runId, setRunId] = useState<string | null>(null)
  const [run, setRun] = useState<RunDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isDownloading, setIsDownloading] = useState(false)
  const [staleWarning, setStaleWarning] = useState<string | null>(null)
  const [lastProgressTime, setLastProgressTime] = useState<number>(Date.now())

  // Get active tab from URL or default to "cards"
  const activeTab = searchParams.get('tab') || 'cards'

  // Unwrap params promise
  useEffect(() => {
    params.then((p) => setRunId(p.runId))
  }, [params])

  // Fetch run details
  useEffect(() => {
    if (!runId) return

    const fetchRun = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const response = await fetch(`/api/pipeline/${runId}`)

        if (response.status === 404) {
          setError('Run not found or you do not have permission to view it.')
          return
        }

        if (!response.ok) {
          throw new Error('Failed to fetch run details')
        }

        const data = await response.json()
        setRun(data)
      } catch (err) {
        console.error('Error fetching run:', err)
        setError(err instanceof Error ? err.message : 'Failed to load run details')
      } finally {
        setIsLoading(false)
      }
    }

    fetchRun()
  }, [runId])

  // Polling for PROCESSING runs with stale detection
  useEffect(() => {
    if (!run || run.status !== 'PROCESSING') return

    let previousStage = run.stageOutputs.filter(s => s.status === 'COMPLETED').length
    let staleCheckCount = 0
    const STALE_THRESHOLD = 12 // 12 polls * 5s = 60 seconds without progress

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/pipeline/${runId}`)
        if (response.ok) {
          const data = await response.json()
          const currentStage = data.stageOutputs.filter((s: StageOutput) => s.status === 'COMPLETED').length

          // Check if pipeline made progress
          if (currentStage > previousStage) {
            previousStage = currentStage
            staleCheckCount = 0
            setStaleWarning(null)
            setLastProgressTime(Date.now())
          } else {
            staleCheckCount++

            // Warn after 60s of no progress
            if (staleCheckCount >= STALE_THRESHOLD) {
              setStaleWarning(
                `Pipeline appears stuck on stage ${previousStage + 1}. The backend may have lost connection. Check backend logs or restart the pipeline.`
              )
            }
          }

          setRun(data)

          // Stop polling if no longer processing
          if (data.status !== 'PROCESSING') {
            clearInterval(pollInterval)
            setStaleWarning(null)
          }
        } else {
          console.error('Polling failed:', response.status, response.statusText)
          setStaleWarning('Failed to fetch pipeline status. Backend may be down.')
        }
      } catch (err) {
        console.error('Polling error:', err)
        setStaleWarning('Network error while fetching status. Check backend connectivity.')
      }
    }, 5000) // Poll every 5 seconds

    return () => clearInterval(pollInterval)
  }, [run, runId])

  // Handle tab change
  const handleTabChange = (value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set('tab', value)
    router.push(`/runs/${runId}?${params.toString()}`, { scroll: false })
  }

  // Handle delete
  const handleDeleteConfirm = async () => {
    if (!runId) return

    setIsDeleting(true)
    try {
      const response = await fetch(`/api/pipeline/${runId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete run')
      }

      toast.success('Run deleted successfully')
      router.push('/runs')
    } catch (error) {
      console.error('Error deleting run:', error)
      toast.error('Failed to delete run. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  // Handle rerun
  const handleRerun = async () => {
    if (!runId) return

    try {
      const response = await fetch(`/api/pipeline/${runId}/rerun`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to rerun pipeline')
      }

      const data = await response.json()
      toast.success('Rerun started successfully')
      router.push(`/pipeline/${data.newRunId}`)
    } catch (error) {
      console.error('Error rerunning pipeline:', error)
      toast.error('Failed to rerun pipeline. Please try again.')
    }
  }

  // Handle PDF download
  const handleDownloadPDF = async () => {
    if (!run) return

    setIsDownloading(true)
    try {
      // TODO: Implement PDF generation
      const { jsPDF } = await import('jspdf')
      const doc = new jsPDF()

      // Add title
      doc.setFontSize(20)
      doc.text('Opportunity Cards', 20, 20)

      // Add metadata
      doc.setFontSize(12)
      doc.text(`Company: ${run.companyName}`, 20, 35)
      doc.text(`Document: ${run.documentName}`, 20, 45)
      doc.text(`Generated: ${new Date(run.createdAt).toLocaleDateString()}`, 20, 55)

      // Add cards
      let yPosition = 70
      run.opportunityCards.forEach((card, index) => {
        if (yPosition > 250) {
          doc.addPage()
          yPosition = 20
        }

        doc.setFontSize(16)
        doc.text(`Card ${card.number}: ${card.title}`, 20, yPosition)
        yPosition += 10

        doc.setFontSize(10)
        const lines = doc.splitTextToSize(card.content, 170)
        doc.text(lines, 20, yPosition)
        yPosition += lines.length * 5 + 15
      })

      doc.save(`${run.documentName}-opportunities.pdf`)
      toast.success('PDF downloaded successfully')
    } catch (error) {
      console.error('Error generating PDF:', error)
      toast.error('Failed to generate PDF. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  // Format duration
  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  }

  // Handle star toggle
  const handleStarToggle = async (cardId: string) => {
    // Store original state for rollback
    const originalCards = run?.opportunityCards || []

    try {
      // Optimistic update BEFORE API call
      setRun((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          opportunityCards: prev.opportunityCards.map((card) =>
            card.id === cardId ? { ...card, isStarred: !card.isStarred } : card
          ),
        }
      })

      const response = await fetch(`/api/cards/${cardId}/star`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to toggle star')
      }

      // Verify server returned correct state
      const data = await response.json()

      // Update with actual server state (in case of race condition)
      setRun((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          opportunityCards: prev.opportunityCards.map((card) =>
            card.id === cardId ? { ...card, isStarred: data.isStarred } : card
          ),
        }
      })

      toast.success('Favorite updated')
    } catch (error) {
      console.error('Error toggling star:', error)

      // ROLLBACK: Restore original state on failure
      setRun((prev) => {
        if (!prev) return prev
        return { ...prev, opportunityCards: originalCards }
      })

      toast.error('Failed to update favorite status. Please try again.')
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white p-6 lg:p-12">
        <div className="max-w-7xl mx-auto space-y-6">
          <Skeleton className="h-6 w-96" />
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    )
  }

  // Error state
  if (error || !run) {
    return (
      <div className="min-h-screen bg-white p-6 lg:p-12">
        <div className="max-w-7xl mx-auto">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'Run not found'}</AlertDescription>
          </Alert>
          <Button onClick={() => router.push('/runs')} className="mt-4">
            Back to Runs
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white p-6 lg:p-12">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Breadcrumbs */}
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/">Home</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink href="/runs">My Runs</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{run.documentName}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        {/* Stale Pipeline Warning */}
        {staleWarning && (
          <Alert variant="destructive" className="border-2 border-red-500">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="font-semibold">
              {staleWarning}
            </AlertDescription>
          </Alert>
        )}

        {/* Header */}
        <div className="border-4 border-black p-6 space-y-4">
          {/* Title */}
          <h1 className="text-3xl font-black">{run.documentName}</h1>

          {/* Metadata Row */}
          <div className="flex flex-wrap gap-3 items-center">
            <Badge className="bg-white border-2 border-black text-black font-semibold px-3 py-1">
              {run.companyName}
            </Badge>
            <span className="text-gray-600">
              {new Date(run.createdAt).toLocaleDateString()} at{' '}
              {new Date(run.createdAt).toLocaleTimeString()}
            </span>
            {run.completedAt && (
              <span className="text-gray-600">Duration: {formatDuration(run.duration)}</span>
            )}
            <span className="text-gray-600">Pipeline v{run.pipelineVersion}</span>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              className="border-2 border-black hover:bg-blue-500 hover:text-white hover:border-blue-500"
              onClick={handleRerun}
              disabled={run.status === 'PROCESSING'}
            >
              <Play className="w-4 h-4 mr-2" />
              Rerun
            </Button>
            <Button
              variant="outline"
              className="border-2 border-black hover:bg-green-500 hover:text-white hover:border-green-500"
              onClick={handleDownloadPDF}
              disabled={isDownloading || run.status !== 'COMPLETED'}
            >
              <Download className="w-4 h-4 mr-2" />
              {isDownloading ? 'Generating...' : 'Download PDF'}
            </Button>
            <Button
              variant="outline"
              className="border-2 border-black hover:bg-red-500 hover:text-white hover:border-red-500"
              onClick={() => setShowDeleteDialog(true)}
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Run
            </Button>
          </div>
        </div>

        {/* Processing Banner */}
        {run.status === 'PROCESSING' && (
          <Alert>
            <AlertCircle className="h-4 h-4" />
            <AlertDescription>
              Pipeline is currently processing. This page will auto-update when complete.
            </AlertDescription>
          </Alert>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <TabsList className="grid w-full grid-cols-3 border-2 border-black">
            <TabsTrigger value="cards" className="font-bold">
              Opportunity Cards
            </TabsTrigger>
            <TabsTrigger value="report" className="font-bold">
              Full Report
            </TabsTrigger>
            <TabsTrigger value="stages" className="font-bold">
              Pipeline Stages
            </TabsTrigger>
          </TabsList>

          <TabsContent value="cards" className="mt-6">
            <RunDetailOpportunityCards
              cards={run.opportunityCards}
              onStarToggle={handleStarToggle}
            />
          </TabsContent>

          <TabsContent value="report" className="mt-6">
            {run.inspirationReport ? (
              <RunDetailFullReport report={run.inspirationReport} />
            ) : (
              <Alert>
                <AlertDescription>No report data available for this run.</AlertDescription>
              </Alert>
            )}
          </TabsContent>

          <TabsContent value="stages" className="mt-6">
            <RunDetailPipelineStages stages={run.stageOutputs} />
          </TabsContent>
        </Tabs>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete this run?</DialogTitle>
            <DialogDescription>
              This will permanently remove the run and all {run.opportunityCards.length} opportunity
              cards. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowDeleteDialog(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

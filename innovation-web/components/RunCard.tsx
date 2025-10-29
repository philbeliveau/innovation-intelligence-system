'use client'

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { SidebarRun } from '@/app/api/pipeline/route'
import { Play, Trash2 } from 'lucide-react'
import { toast } from 'sonner'

interface RunCardProps {
  run: SidebarRun
  onDelete: (id: string) => void
  onRerun: (id: string) => void
}

// Color schemes for random assignment (matching UploadHistoryCard)
const COLOR_SCHEMES = [
  { from: '#FFB6C1', to: '#FF6B6B' }, // Pink to Red
  { from: '#A7C7E7', to: '#4682B4' }, // Light Blue to Steel Blue
  { from: '#DDA0DD', to: '#BA55D3' }, // Plum to Medium Orchid
  { from: '#98FB98', to: '#3CB371' }, // Pale Green to Medium Sea Green
  { from: '#FFD700', to: '#FF8C00' }, // Gold to Dark Orange
  { from: '#F0E68C', to: '#BDB76B' }, // Khaki to Dark Khaki
]

// Simple hash function to generate consistent index from string
function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash)
}

export default function RunCard({ run, onDelete, onRerun }: RunCardProps) {
  const router = useRouter()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showRerunDialog, setShowRerunDialog] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isRerunning, setIsRerunning] = useState(false)
  const [pdfThumbnail, setPdfThumbnail] = useState<string | null>(null)
  const [isLoadingPdf, setIsLoadingPdf] = useState(true)

  // Generate consistent color scheme based on document name
  const colorScheme = useMemo(() => {
    const hash = hashString(run.documentName)
    const colorIndex = hash % COLOR_SCHEMES.length
    return COLOR_SCHEMES[colorIndex]
  }, [run.documentName])

  // Generate PDF thumbnail if blob URL is available
  useEffect(() => {
    if (!run.blobUrl) {
      console.log('[RunCard] No blobUrl provided for:', run.documentName)
      setIsLoadingPdf(false)
      return
    }

    console.log('[RunCard] Loading PDF thumbnail from:', run.blobUrl)

    const loadPdfThumbnail = async () => {
      try {
        // Dynamically import pdf.js - use webpack build for Next.js
        const pdfjsLib = await import('pdfjs-dist/webpack.mjs')
        console.log('[RunCard] PDF.js loaded, version:', pdfjsLib.version)

        const loadingTask = pdfjsLib.getDocument(run.blobUrl!)
        console.log('[RunCard] Loading document...')

        const pdf = await loadingTask.promise
        console.log('[RunCard] PDF loaded, pages:', pdf.numPages)

        const page = await pdf.getPage(1)
        console.log('[RunCard] First page loaded')

        const viewport = page.getViewport({ scale: 0.5 })
        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')

        if (!context) {
          console.error('[RunCard] Failed to get canvas context')
          setIsLoadingPdf(false)
          return
        }

        canvas.height = viewport.height
        canvas.width = viewport.width
        console.log('[RunCard] Canvas size:', canvas.width, 'x', canvas.height)

        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        await page.render({
          canvasContext: context,
          viewport: viewport,
        } as any).promise

        console.log('[RunCard] Page rendered to canvas')

        const dataUrl = canvas.toDataURL()
        console.log('[RunCard] Thumbnail generated, length:', dataUrl.length)
        setPdfThumbnail(dataUrl)
        setIsLoadingPdf(false)
      } catch (error) {
        console.error('[RunCard] Failed to generate PDF thumbnail:', error)
        // Fallback to white background
        setPdfThumbnail(null)
        setIsLoadingPdf(false)
      }
    }

    loadPdfThumbnail()
  }, [run.blobUrl, run.documentName])

  const getStatusBadge = (status: SidebarRun['status']) => {
    const styles = {
      COMPLETED: 'bg-green-100 text-green-800 border-green-300',
      PROCESSING: 'bg-blue-100 text-blue-800 border-blue-300',
      FAILED: 'bg-red-100 text-red-800 border-red-300',
      CANCELLED: 'bg-gray-100 text-gray-800 border-gray-300',
    }
    return {
      style: styles[status] || styles.CANCELLED,
      label: status.charAt(0) + status.slice(1).toLowerCase(),
    }
  }

  const getRelativeDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const handleView = () => {
    router.push(`/runs/${run.id}`)
  }

  // Truncate document name for display
  const displayName = run.documentName.length > 35
    ? `${run.documentName.substring(0, 35)}...`
    : run.documentName

  const statusBadge = getStatusBadge(run.status)

  const handleDeleteConfirm = async () => {
    setIsDeleting(true)
    try {
      const response = await fetch(`/api/pipeline/${run.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete run')
      }

      toast.success('Run deleted successfully')
      onDelete(run.id)
      setShowDeleteDialog(false)
    } catch (error) {
      console.error('Error deleting run:', error)
      toast.error('Failed to delete run. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleRerunConfirm = async () => {
    setIsRerunning(true)
    try {
      const response = await fetch(`/api/pipeline/${run.id}/rerun`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to rerun pipeline')
      }

      const data = await response.json()
      toast.success('Rerun started successfully')
      onRerun(data.newRunId)
      setShowRerunDialog(false)
      router.push(`/pipeline/${data.newRunId}`)
    } catch (error) {
      console.error('Error rerunning pipeline:', error)
      toast.error('Failed to rerun pipeline. Please try again.')
    } finally {
      setIsRerunning(false)
    }
  }

  return (
    <>
      <article
        role="button"
        tabIndex={0}
        onClick={handleView}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            handleView()
          }
        }}
        aria-label={`View run for ${run.documentName}, ${statusBadge.label}`}
        className="
          group
          relative
          bg-white
          rounded-lg
          shadow-sm
          border border-gray-200
          overflow-hidden
          h-[400px]
          flex flex-col
          cursor-pointer
          hover:shadow-md
          transition-shadow
          focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
        "
      >
        {/* Delete button */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            setShowDeleteDialog(true)
          }}
          aria-label="Delete run"
          className="
            absolute top-3 right-3
            w-8 h-8
            flex items-center justify-center
            bg-white/90
            backdrop-blur-sm
            rounded-full
            border border-gray-300
            text-gray-600
            hover:bg-red-50 hover:text-red-600 hover:border-red-300
            transition-colors
            focus:outline-none focus:ring-2 focus:ring-red-500 z-10
          "
        >
          <Trash2 className="w-4 h-4" />
        </button>

        {/* Hero Image with PDF thumbnail */}
        <div className="relative w-full flex-1">
          {(isLoadingPdf || !pdfThumbnail) ? (
            /* Loading skeleton - stay white until thumbnail is ready */
            <div className="relative w-full h-full bg-white animate-pulse">
              <div className="absolute inset-0 bg-white" />
              <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-4 z-20">
                <div className="mb-1.5">
                  <div className="inline-block h-4 w-24 bg-gray-200 rounded" />
                </div>
                <div className="h-4 w-3/4 bg-gray-200 rounded" />
              </div>
            </div>
          ) : (
            <div className="relative w-full h-full overflow-hidden bg-white">
              {/* PDF thumbnail - extremely light blur */}
              <div className="absolute inset-0">
                <img
                  src={pdfThumbnail}
                  alt="Document preview"
                  className="w-full h-full object-cover blur-sm"
                />
              </div>

              {/* Title overlay with status badge and category */}
              <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-4 z-20">
                <div className="mb-1.5 flex items-center gap-2 flex-wrap">
                  <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded border ${statusBadge.style}`}>
                    {statusBadge.label}
                  </span>
                  {run.status === 'COMPLETED' && run.cardCount > 0 && (
                    <span className="inline-block text-xs text-gray-600">
                      {run.cardCount} cards
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-900 font-medium leading-relaxed">
                  {displayName}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Bottom info section */}
        <div className="p-4 bg-white border-t border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-gray-900">{run.companyName}</p>
            <span className="text-xs text-gray-500">
              {getRelativeDate(run.createdAt)}
            </span>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              setShowRerunDialog(true)
            }}
            className="w-full border-gray-300 hover:bg-gray-50"
          >
            <Play className="w-3 h-3 mr-2" />
            Rerun Pipeline
          </Button>
        </div>
      </article>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete this run?</DialogTitle>
            <DialogDescription>
              This will permanently remove the run and all {run.cardCount || 0} opportunity cards.
              This action cannot be undone.
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
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Rerun Confirmation Dialog */}
      <Dialog open={showRerunDialog} onOpenChange={setShowRerunDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rerun Pipeline</DialogTitle>
            <DialogDescription>
              This will create a new pipeline run with the same document and company settings.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowRerunDialog(false)}
              disabled={isRerunning}
            >
              Cancel
            </Button>
            <Button onClick={handleRerunConfirm} disabled={isRerunning}>
              {isRerunning ? 'Starting...' : 'Start Rerun'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

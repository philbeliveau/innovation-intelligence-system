'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { SidebarRun } from '@/app/api/runs/route'
import { Eye, Play, Trash2 } from 'lucide-react'

interface RunCardProps {
  run: SidebarRun
  onDelete: (id: string) => void
  onRerun: (id: string) => void
}

export default function RunCard({ run, onDelete, onRerun }: RunCardProps) {
  const router = useRouter()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [showRerunDialog, setShowRerunDialog] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isRerunning, setIsRerunning] = useState(false)

  const getStatusColor = (status: SidebarRun['status']) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-green-500'
      case 'PROCESSING':
        return 'bg-blue-500'
      case 'FAILED':
        return 'bg-red-500'
      case 'CANCELLED':
        return 'bg-gray-500'
      default:
        return 'bg-gray-500'
    }
  }

  const getStatusLabel = (status: SidebarRun['status']) => {
    return status.charAt(0) + status.slice(1).toLowerCase()
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

  const handleDeleteConfirm = async () => {
    setIsDeleting(true)
    try {
      const response = await fetch(`/api/runs/${run.id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Failed to delete run')
      }

      onDelete(run.id)
      setShowDeleteDialog(false)
    } catch (error) {
      console.error('Error deleting run:', error)
      alert('Failed to delete run. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleRerunConfirm = async () => {
    setIsRerunning(true)
    try {
      const response = await fetch(`/api/runs/${run.id}/rerun`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error('Failed to rerun pipeline')
      }

      const data = await response.json()
      onRerun(data.newRunId)
      setShowRerunDialog(false)
      router.push(`/pipeline/${data.newRunId}`)
    } catch (error) {
      console.error('Error rerunning pipeline:', error)
      alert('Failed to rerun pipeline. Please try again.')
    } finally {
      setIsRerunning(false)
    }
  }

  return (
    <>
      <Card
        className="border-[5px] border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all duration-200 hover:-translate-x-[3px] hover:-translate-y-[3px] hover:shadow-[11px_11px_0px_0px_rgba(0,0,0,1)] cursor-pointer"
        onClick={handleView}
      >
        <CardContent className="p-6 space-y-4">
          {/* Document Name */}
          <h3 className="font-bold text-lg truncate">{run.documentName}</h3>

          {/* Company Badge */}
          <Badge className="bg-white border-2 border-black text-black font-semibold px-3 py-1">
            {run.companyName}
          </Badge>

          {/* Status and Date Row */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${getStatusColor(run.status)}`} />
              <span className="text-gray-700">{getStatusLabel(run.status)}</span>
            </div>
            <span className="text-gray-500">{getRelativeDate(run.createdAt)}</span>
          </div>

          {/* Metrics Row */}
          {run.status === 'COMPLETED' && (
            <div className="text-sm text-gray-600">
              {run.cardCount} cards
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-2" onClick={(e) => e.stopPropagation()}>
            <Button
              variant="outline"
              size="sm"
              className="flex-1 border-2 border-black hover:bg-black hover:text-white"
              onClick={handleView}
            >
              <Eye className="w-4 h-4 mr-1" />
              View
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex-1 border-2 border-black hover:bg-blue-500 hover:text-white hover:border-blue-500"
              onClick={(e) => {
                e.stopPropagation()
                setShowRerunDialog(true)
              }}
            >
              <Play className="w-4 h-4 mr-1" />
              Rerun
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="border-2 border-black hover:bg-red-500 hover:text-white hover:border-red-500"
              onClick={(e) => {
                e.stopPropagation()
                setShowDeleteDialog(true)
              }}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Pipeline Run</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this run? This action cannot be undone.
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

'use client'

// Innovation Intelligence System - Duplicate Upload Dialog Component
// Dialog shown when user attempts to upload a file that already exists

import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import type { UploadMetadata } from '@/lib/upload-history'

interface DuplicateUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  duplicateUpload: UploadMetadata | null
  onUploadAnyway?: () => void
}

export function DuplicateUploadDialog({
  open,
  onOpenChange,
  duplicateUpload,
  onUploadAnyway,
}: DuplicateUploadDialogProps) {
  const router = useRouter()

  if (!duplicateUpload) return null

  // Format upload date
  const uploadDate = new Date(duplicateUpload.uploaded_at)
  const formattedDate = uploadDate.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  const handleViewAnalysis = () => {
    onOpenChange(false)
    router.push(`/analyze/${duplicateUpload.upload_id}`)
  }

  const handleUploadAnyway = () => {
    onOpenChange(false)
    onUploadAnyway?.()
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-2">
            {/* Warning icon */}
            <div className="w-12 h-12 rounded-full bg-yellow-100 flex items-center justify-center flex-shrink-0">
              <svg
                className="w-6 h-6 text-yellow-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4"
                />
              </svg>
            </div>
            <div>
              <DialogTitle className="text-left">
                Document Already Uploaded
              </DialogTitle>
              <p className="text-sm text-gray-500 mt-1">
                This file has been uploaded before
              </p>
            </div>
          </div>
        </DialogHeader>

        <DialogDescription asChild>
          <div className="space-y-4">
            {/* Document info */}
            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Filename
                </p>
                <p className="text-sm text-gray-900 font-medium mt-1 break-all">
                  {duplicateUpload.filename}
                </p>
              </div>

              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  Previously Uploaded
                </p>
                <p className="text-sm text-gray-900 mt-1">{formattedDate}</p>
              </div>
            </div>

            {/* Explanation */}
            <p className="text-sm text-gray-600">
              The system detected that this document has identical content to a
              previously uploaded file. Would you like to view the existing
              analysis instead?
            </p>
          </div>
        </DialogDescription>

        <DialogFooter className="flex-col sm:flex-row gap-2 sm:gap-0">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>

          {onUploadAnyway && (
            <Button
              variant="outline"
              onClick={handleUploadAnyway}
              className="w-full sm:w-auto border-gray-300 hover:bg-gray-50"
            >
              Upload Anyway
            </Button>
          )}

          <Button
            onClick={handleViewAnalysis}
            className="w-full sm:w-auto bg-[#5B9A99] hover:bg-[#4A8988] text-white"
          >
            View Existing Analysis
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

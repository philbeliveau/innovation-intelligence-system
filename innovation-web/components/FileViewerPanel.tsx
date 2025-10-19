'use client'

import { useState } from 'react'
import { Download, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from '@/components/ui/sheet'

interface FileViewerPanelProps {
  isOpen: boolean
  onClose: () => void
  blobUrl: string
  fileName: string
}

export function FileViewerPanel({
  isOpen,
  onClose,
  blobUrl,
  fileName,
}: FileViewerPanelProps) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleRetry = () => {
    setError(false)
    setLoading(true)
  }

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent
        side="right"
        className="w-full p-0 md:w-[60vw] md:min-w-[500px] md:max-w-[800px]"
      >
        {/* Header */}
        <SheetHeader className="sticky top-0 z-10 flex flex-row items-center justify-between border-b bg-white px-6 py-4">
          <SheetTitle className="flex-1 truncate pr-4 text-lg font-semibold">
            {fileName}
          </SheetTitle>
          <SheetDescription className="sr-only">
            PDF document viewer. Use download button to save file or close button to return to analysis.
          </SheetDescription>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDownload}
              aria-label="Download file"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              aria-label="Close panel"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        {/* Content */}
        <div className="relative h-[calc(100vh-73px)]">
          {/* Loading State */}
          {loading && !error && (
            <div className="flex h-full items-center justify-center">
              <div className="flex flex-col items-center gap-4">
                <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-[#4A9B8E]" />
                <p className="text-sm text-gray-600">Loading PDF...</p>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="flex h-full items-center justify-center">
              <div className="max-w-md space-y-4 text-center">
                <div className="text-6xl">⚠️</div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Failed to load document
                </h3>
                <p className="text-sm text-gray-600">
                  Your browser cannot display PDFs inline. Please download the file
                  to view it.
                </p>
                <div className="flex justify-center gap-3">
                  <Button onClick={handleDownload} variant="default">
                    Download PDF
                  </Button>
                  <Button onClick={handleRetry} variant="outline">
                    Try Again
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* PDF Viewer (lazy loaded) */}
          {isOpen && !error && (
            <iframe
              src={blobUrl}
              title={`PDF viewer: ${fileName}`}
              className="h-full w-full border-0"
              onLoad={() => setLoading(false)}
              onError={() => {
                setLoading(false)
                setError(true)
              }}
            />
          )}
        </div>

        {/* Screen Reader Text */}
        <span className="sr-only">
          Press Escape to close the file viewer panel
        </span>
      </SheetContent>
    </Sheet>
  )
}

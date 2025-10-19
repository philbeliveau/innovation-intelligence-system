'use client'

// Innovation Intelligence System - Upload History Section Component
// Section container displaying upload history cards with horizontal scroll

import { useState, useEffect } from 'react'
import { getUploadHistory, removeUploadFromHistory } from '@/lib/upload-history'
import type { UploadMetadata } from '@/lib/upload-history'
import { UploadHistoryCard } from './UploadHistoryCard'

interface UploadHistorySectionProps {
  companyId: string
  onHistoryUpdate?: () => void // Callback to notify parent of history changes
}

export function UploadHistorySection({ companyId, onHistoryUpdate }: UploadHistorySectionProps) {
  const [history, setHistory] = useState<UploadMetadata[]>([])

  // Load history on mount and when company changes
  useEffect(() => {
    const loadHistory = () => {
      const uploads = getUploadHistory(companyId)
      setHistory(uploads)
    }
    loadHistory()
  }, [companyId])

  const loadHistory = () => {
    const uploads = getUploadHistory(companyId)
    setHistory(uploads)
  }

  // Handle delete from history
  const handleDelete = (uploadId: string) => {
    removeUploadFromHistory(companyId, uploadId)
    loadHistory() // Reload history after deletion
    onHistoryUpdate?.() // Notify parent
  }

  // Don't render section if no history
  if (history.length === 0) {
    return null
  }

  return (
    <section className="w-full mt-12 mb-8">
      {/* Horizontal scrollable card container - centered */}
      <div className="relative flex justify-center">
        <div
          className="
            flex gap-4
            overflow-x-auto
            pb-4
            scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100
            snap-x snap-mandatory
            md:grid md:grid-cols-2 md:overflow-x-visible lg:grid-cols-3
            justify-items-center
          "
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: '#CBD5E0 #F7FAFC'
          }}
        >
          {history.map((upload) => (
            <div key={upload.upload_id} className="snap-start">
              <UploadHistoryCard
                upload={upload}
                onDelete={handleDelete}
              />
            </div>
          ))}
        </div>

        {/* Scroll indicators for mobile (when more than 4 cards) */}
        {history.length > 4 && (
          <div className="md:hidden flex justify-center gap-1 mt-2">
            {history.slice(0, 4).map((_, index) => (
              <div
                key={index}
                className="w-2 h-2 rounded-full bg-gray-300"
                aria-hidden="true"
              />
            ))}
            {history.length > 4 && (
              <div className="text-xs text-gray-500 ml-1">
                +{history.length - 4} more
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}

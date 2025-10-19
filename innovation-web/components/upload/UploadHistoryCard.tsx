'use client'

// Innovation Intelligence System - Upload History Card Component
// Individual card displaying upload metadata with navigation

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import type { UploadMetadata } from '@/lib/upload-history'
import { formatRelativeTime } from '@/lib/format-relative-time'

interface UploadHistoryCardProps {
  upload: UploadMetadata
  onDelete?: (uploadId: string) => void
}

export function UploadHistoryCard({ upload, onDelete }: UploadHistoryCardProps) {
  const router = useRouter()
  const [relativeTime, setRelativeTime] = useState('')

  // Update relative time on mount and every minute
  useEffect(() => {
    const updateTime = () => {
      setRelativeTime(formatRelativeTime(upload.uploaded_at))
    }

    updateTime()
    const interval = setInterval(updateTime, 60000) // Update every 60 seconds

    return () => clearInterval(interval)
  }, [upload.uploaded_at])

  // Truncate filename for display
  const displayFilename = upload.filename.length > 35
    ? `${upload.filename.substring(0, 35)}...`
    : upload.filename

  // Get current month and year
  const uploadDate = new Date(upload.uploaded_at)
  const monthYear = uploadDate.toLocaleString('en-US', { month: 'long', year: 'numeric' }).toUpperCase()

  // Handle card click - navigate to analysis page
  const handleClick = () => {
    router.push(`/analyze/${upload.upload_id}`)
  }

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  // Handle delete click (optional)
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card navigation
    if (onDelete) {
      onDelete(upload.upload_id)
    }
  }

  return (
    <article
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      aria-label={`Navigate to ${upload.filename}, uploaded ${relativeTime}`}
      className="
        group
        relative
        flex-shrink-0
        w-[300px]
        bg-white
        border-[6px] border-black
        shadow-[12px_12px_0_0_#000]
        cursor-pointer
        transition-all duration-300
        hover:-translate-x-[5px] hover:-translate-y-[5px]
        hover:shadow-[17px_17px_0_0_#000]
        focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-offset-2
        select-none
      "
    >
      {/* Optional delete button */}
      {onDelete && (
        <button
          onClick={handleDelete}
          aria-label="Remove from history"
          className="
            absolute top-3 left-3
            w-8 h-8
            flex items-center justify-center
            bg-white
            rounded-full
            border-2 border-black
            text-black
            hover:bg-black hover:text-white
            transition-colors
            focus:outline-none focus:ring-2 focus:ring-black z-10
          "
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      {/* Decorative background graphic */}
      <div className="relative overflow-hidden h-[200px] bg-gradient-to-br from-pink-200 via-pink-300 to-coral-300">
        {/* Abstract wave shapes */}
        <div className="absolute inset-0">
          <svg className="absolute w-full h-full" viewBox="0 0 300 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: '#FFB6C1', stopOpacity: 1}} />
                <stop offset="100%" style={{stopColor: '#FF6B6B', stopOpacity: 1}} />
              </linearGradient>
              <linearGradient id="grad2" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" style={{stopColor: '#FFA07A', stopOpacity: 0.8}} />
                <stop offset="100%" style={{stopColor: '#FA8072', stopOpacity: 0.6}} />
              </linearGradient>
            </defs>

            {/* Wave shapes */}
            <ellipse cx="250" cy="80" rx="120" ry="100" fill="url(#grad1)" opacity="0.7" />
            <ellipse cx="80" cy="150" rx="100" ry="80" fill="url(#grad2)" opacity="0.6" />
            <circle cx="200" cy="160" r="60" fill="#FFB6C1" opacity="0.5" />
          </svg>
        </div>

        {/* Content overlay */}
        <div className="relative p-5 h-full flex flex-col">
          {/* Top section */}
          <div className="mb-auto">
            <div className="text-xs font-bold text-black/70 mb-2">
              {monthYear}
            </div>
            <div className="text-lg font-black text-black uppercase mb-1">
              Food & Beverage
            </div>
            <div className="flex items-center gap-1 text-xs font-bold text-black/60">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V9.99h7V2.95l8 3.98v7.06h-8z"/>
              </svg>
              <span className="uppercase tracking-wide">Serendipity Seekers</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom white section */}
      <div className="p-5 bg-white border-t-[3px] border-black">
        <h3 className="text-base font-black text-black uppercase mb-2 leading-tight">
          {displayFilename}
        </h3>
        <p className="text-sm text-black/70 line-clamp-2">
          New value systems emerge as both brands and consumers redefine how worth is created and recognized.
        </p>
        <div className="mt-3 text-xs text-black/50 font-medium">
          {relativeTime}
        </div>
      </div>
    </article>
  )
}

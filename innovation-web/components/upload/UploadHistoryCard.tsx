'use client'

// Innovation Intelligence System - Upload History Card Component
// Individual card displaying upload metadata with navigation

import { useState, useEffect, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import type { UploadMetadata } from '@/lib/upload-history'
import { formatRelativeTime } from '@/lib/format-relative-time'

interface UploadHistoryCardProps {
  upload: UploadMetadata
  onDelete?: (uploadId: string) => void
}

// Color schemes for random assignment
const COLOR_SCHEMES = [
  {
    from: '#FFB6C1',
    via: '#FFB6C1',
    to: '#FF6B6B',
    grad1Start: '#FFB6C1',
    grad1End: '#FF6B6B',
    grad2Start: '#FFA07A',
    grad2End: '#FA8072',
    circle: '#FFB6C1',
  },
  {
    from: '#A7C7E7',
    via: '#87CEEB',
    to: '#4682B4',
    grad1Start: '#A7C7E7',
    grad1End: '#4682B4',
    grad2Start: '#6CA6CD',
    grad2End: '#5F9EA0',
    circle: '#87CEEB',
  },
  {
    from: '#DDA0DD',
    via: '#DA70D6',
    to: '#BA55D3',
    grad1Start: '#DDA0DD',
    grad1End: '#BA55D3',
    grad2Start: '#D8BFD8',
    grad2End: '#9370DB',
    circle: '#DA70D6',
  },
  {
    from: '#98FB98',
    via: '#90EE90',
    to: '#3CB371',
    grad1Start: '#98FB98',
    grad1End: '#3CB371',
    grad2Start: '#8FBC8F',
    grad2End: '#2E8B57',
    circle: '#90EE90',
  },
  {
    from: '#FFD700',
    via: '#FFA500',
    to: '#FF8C00',
    grad1Start: '#FFD700',
    grad1End: '#FF8C00',
    grad2Start: '#FFDB58',
    grad2End: '#FF7F00',
    circle: '#FFA500',
  },
  {
    from: '#F0E68C',
    via: '#EEE8AA',
    to: '#BDB76B',
    grad1Start: '#F0E68C',
    grad1End: '#BDB76B',
    grad2Start: '#F5DEB3',
    grad2End: '#DAA520',
    circle: '#EEE8AA',
  },
]

// Generate description based on filename with enhanced keyword detection
function generateDescription(filename: string): string {
  const lowerName = filename.toLowerCase()

  // Trend & Reports
  if (lowerName.includes('trend') || lowerName.includes('report') || lowerName.includes('forecast')) {
    return 'Emerging trends and shifts in consumer behavior and market dynamics.'
  }

  // Research & Studies
  if (lowerName.includes('research') || lowerName.includes('study') || lowerName.includes('whitepaper') || lowerName.includes('white paper')) {
    return 'Research insights revealing new opportunities and market possibilities.'
  }

  // News & Articles
  if (lowerName.includes('article') || lowerName.includes('news') || lowerName.includes('press') || lowerName.includes('story')) {
    return 'News and analysis exploring innovative approaches and industry developments.'
  }

  // Analysis & Deep Dives
  if (lowerName.includes('analysis') || lowerName.includes('insight') || lowerName.includes('deep dive') || lowerName.includes('deepdive')) {
    return 'Deep analysis uncovering patterns and opportunities in the market landscape.'
  }

  // Innovation & Ideas
  if (lowerName.includes('innovation') || lowerName.includes('idea') || lowerName.includes('concept') || lowerName.includes('future')) {
    return 'Innovation concepts and ideas driving new value creation possibilities.'
  }

  // Consumer & Customer Focus
  if (lowerName.includes('consumer') || lowerName.includes('customer') || lowerName.includes('user') || lowerName.includes('audience')) {
    return 'Consumer insights revealing evolving needs and behavioral patterns.'
  }

  // Market Intelligence
  if (lowerName.includes('market') || lowerName.includes('industry') || lowerName.includes('sector') || lowerName.includes('landscape')) {
    return 'Market intelligence highlighting emerging opportunities and competitive shifts.'
  }

  // Strategy & Planning
  if (lowerName.includes('strategy') || lowerName.includes('plan') || lowerName.includes('roadmap') || lowerName.includes('framework')) {
    return 'Strategic perspectives on navigating market changes and opportunities.'
  }

  // Data & Metrics
  if (lowerName.includes('data') || lowerName.includes('metric') || lowerName.includes('stat') || lowerName.includes('survey')) {
    return 'Data-driven insights revealing patterns and opportunities in market behavior.'
  }

  // Competitive Intelligence
  if (lowerName.includes('competit') || lowerName.includes('benchmark') || lowerName.includes('comparison')) {
    return 'Competitive intelligence uncovering strategic positioning and market gaps.'
  }

  // Technology & Digital
  if (lowerName.includes('tech') || lowerName.includes('digital') || lowerName.includes('ai') || lowerName.includes('automation')) {
    return 'Technology insights exploring digital transformation and innovation opportunities.'
  }

  // Case Studies & Examples
  if (lowerName.includes('case') || lowerName.includes('example') || lowerName.includes('success')) {
    return 'Real-world examples and case studies demonstrating innovative approaches.'
  }

  // Default fallback
  return 'Insights and perspectives revealing new opportunities for value creation.'
}

// Extract category from filename with enhanced keyword detection
function extractCategory(filename: string): string {
  const lowerName = filename.toLowerCase()

  // Food & Beverage
  if (lowerName.includes('food') || lowerName.includes('beverage') || lowerName.includes('restaurant') ||
      lowerName.includes('culinary') || lowerName.includes('drink') || lowerName.includes('nutrition') ||
      lowerName.includes('meal') || lowerName.includes('recipe')) {
    return 'Food & Beverage'
  }

  // Technology & Digital
  if (lowerName.includes('tech') || lowerName.includes('digital') || lowerName.includes('software') ||
      lowerName.includes('ai') || lowerName.includes('automation') || lowerName.includes('cyber') ||
      lowerName.includes('cloud') || lowerName.includes('data') || lowerName.includes('algorithm') ||
      lowerName.includes('machine learning') || lowerName.includes('blockchain')) {
    return 'Technology'
  }

  // Health & Wellness
  if (lowerName.includes('health') || lowerName.includes('wellness') || lowerName.includes('medical') ||
      lowerName.includes('fitness') || lowerName.includes('pharma') || lowerName.includes('care') ||
      lowerName.includes('therapy') || lowerName.includes('mental') || lowerName.includes('clinic')) {
    return 'Health & Wellness'
  }

  // Retail & E-commerce
  if (lowerName.includes('retail') || lowerName.includes('commerce') || lowerName.includes('store') ||
      lowerName.includes('shop') || lowerName.includes('ecommerce') || lowerName.includes('e-commerce') ||
      lowerName.includes('marketplace') || lowerName.includes('merchant')) {
    return 'Retail & Commerce'
  }

  // Financial Services
  if (lowerName.includes('finance') || lowerName.includes('bank') || lowerName.includes('fintech') ||
      lowerName.includes('invest') || lowerName.includes('payment') || lowerName.includes('credit') ||
      lowerName.includes('insurance') || lowerName.includes('wealth') || lowerName.includes('trading')) {
    return 'Financial Services'
  }

  // Fashion & Apparel
  if (lowerName.includes('fashion') || lowerName.includes('apparel') || lowerName.includes('clothing') ||
      lowerName.includes('textile') || lowerName.includes('luxury') || lowerName.includes('beauty') ||
      lowerName.includes('cosmetic') || lowerName.includes('style')) {
    return 'Fashion & Apparel'
  }

  // Energy & Sustainability
  if (lowerName.includes('energy') || lowerName.includes('sustainability') || lowerName.includes('renewable') ||
      lowerName.includes('green') || lowerName.includes('climate') || lowerName.includes('environment') ||
      lowerName.includes('carbon') || lowerName.includes('solar') || lowerName.includes('wind')) {
    return 'Energy & Sustainability'
  }

  // Automotive & Mobility
  if (lowerName.includes('auto') || lowerName.includes('vehicle') || lowerName.includes('car') ||
      lowerName.includes('mobility') || lowerName.includes('transport') || lowerName.includes('ev') ||
      lowerName.includes('electric vehicle') || lowerName.includes('autonomous')) {
    return 'Automotive'
  }

  // Travel & Hospitality
  if (lowerName.includes('travel') || lowerName.includes('hospitality') || lowerName.includes('hotel') ||
      lowerName.includes('tourism') || lowerName.includes('airline') || lowerName.includes('vacation') ||
      lowerName.includes('destination') || lowerName.includes('cruise')) {
    return 'Travel & Hospitality'
  }

  // Media & Entertainment
  if (lowerName.includes('media') || lowerName.includes('entertainment') || lowerName.includes('content') ||
      lowerName.includes('streaming') || lowerName.includes('gaming') || lowerName.includes('music') ||
      lowerName.includes('video') || lowerName.includes('film') || lowerName.includes('publishing')) {
    return 'Media & Entertainment'
  }

  // Education & Learning
  if (lowerName.includes('education') || lowerName.includes('learning') || lowerName.includes('training') ||
      lowerName.includes('academic') || lowerName.includes('school') || lowerName.includes('university') ||
      lowerName.includes('course') || lowerName.includes('edtech')) {
    return 'Education & Learning'
  }

  // Real Estate & Construction
  if (lowerName.includes('real estate') || lowerName.includes('property') || lowerName.includes('construction') ||
      lowerName.includes('housing') || lowerName.includes('building') || lowerName.includes('architect')) {
    return 'Real Estate'
  }

  // Manufacturing & Supply Chain
  if (lowerName.includes('manufact') || lowerName.includes('supply chain') || lowerName.includes('logistics') ||
      lowerName.includes('warehouse') || lowerName.includes('production') || lowerName.includes('industrial')) {
    return 'Manufacturing'
  }

  // Agriculture & Food Production
  if (lowerName.includes('agricult') || lowerName.includes('farm') || lowerName.includes('agri') ||
      lowerName.includes('crop') || lowerName.includes('livestock')) {
    return 'Agriculture'
  }

  // Telecommunications
  if (lowerName.includes('telecom') || lowerName.includes('network') || lowerName.includes('5g') ||
      lowerName.includes('wireless') || lowerName.includes('communication')) {
    return 'Telecommunications'
  }

  // Default fallback
  return 'Innovation Research'
}

// Simple hash function to generate consistent index from string
function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32-bit integer
  }
  return Math.abs(hash)
}

export function UploadHistoryCard({ upload, onDelete }: UploadHistoryCardProps) {
  const router = useRouter()
  const [relativeTime, setRelativeTime] = useState('')
  const [pdfThumbnail, setPdfThumbnail] = useState<string | null>(null)
  const [isLoadingPdf, setIsLoadingPdf] = useState(true)

  // Generate consistent color scheme and content based on filename
  const { colorScheme, category, description } = useMemo(() => {
    const hash = hashString(upload.filename)
    const colorIndex = hash % COLOR_SCHEMES.length

    return {
      colorScheme: COLOR_SCHEMES[colorIndex],
      category: extractCategory(upload.filename),
      description: generateDescription(upload.filename),
    }
  }, [upload.filename])

  // Generate PDF thumbnail for background
  useEffect(() => {
    if (!upload.blob_url) {
      console.log('[UploadHistoryCard] No blob_url provided')
      return
    }

    console.log('[UploadHistoryCard] Loading PDF thumbnail from:', upload.blob_url)

    const loadPdfThumbnail = async () => {
      try {
        // Dynamically import pdf.js - use webpack build for Next.js
        const pdfjsLib = await import('pdfjs-dist/webpack.mjs')
        console.log('[UploadHistoryCard] PDF.js loaded, version:', pdfjsLib.version)

        const loadingTask = pdfjsLib.getDocument(upload.blob_url)
        console.log('[UploadHistoryCard] Loading document...')

        const pdf = await loadingTask.promise
        console.log('[UploadHistoryCard] PDF loaded, pages:', pdf.numPages)

        const page = await pdf.getPage(1)
        console.log('[UploadHistoryCard] First page loaded')

        const viewport = page.getViewport({ scale: 0.5 })
        const canvas = document.createElement('canvas')
        const context = canvas.getContext('2d')

        if (!context) {
          console.error('[UploadHistoryCard] Failed to get canvas context')
          setIsLoadingPdf(false)
          return
        }

        canvas.height = viewport.height
        canvas.width = viewport.width
        console.log('[UploadHistoryCard] Canvas size:', canvas.width, 'x', canvas.height)

        // @ts-expect-error - pdfjs-dist types are incomplete
        await page.render({
          canvasContext: context,
          viewport: viewport,
        }).promise

        console.log('[UploadHistoryCard] Page rendered to canvas')

        const dataUrl = canvas.toDataURL()
        console.log('[UploadHistoryCard] Thumbnail generated, length:', dataUrl.length)
        setPdfThumbnail(dataUrl)
        setIsLoadingPdf(false)
      } catch (error) {
        console.error('[UploadHistoryCard] Failed to generate PDF thumbnail:', error)
        // Fallback to just gradient
        setPdfThumbnail(null)
        setIsLoadingPdf(false)
      }
    }

    loadPdfThumbnail()
  }, [upload.blob_url])

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
      {/* Optional delete button */}
      {onDelete && (
        <button
          onClick={handleDelete}
          aria-label="Remove from history"
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
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      {/* Hero Image with PDF thumbnail or loading skeleton */}
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

            {/* Title overlay at bottom with category badge */}
            <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-4 z-20">
              <div className="mb-1.5">
                <span className="inline-block text-xs font-semibold text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                  {category}
                </span>
              </div>
              <p className="text-sm text-gray-900 font-medium leading-relaxed">
                {displayFilename}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Bottom white section */}
      <div className="p-4 bg-white border-t border-gray-100">
        {(isLoadingPdf || !pdfThumbnail) ? (
          /* Loading skeleton for bottom section */
          <div className="animate-pulse">
            <div className="h-3 w-full bg-gray-200 rounded mb-1" />
            <div className="h-3 w-4/5 bg-gray-200 rounded mb-2" />
            <div className="h-3 w-16 bg-gray-200 rounded" />
          </div>
        ) : (
          <>
            <p className="text-sm text-gray-700 line-clamp-2 mb-2">
              {description}
            </p>
            <div className="text-xs text-gray-500 font-medium">
              {relativeTime}
            </div>
          </>
        )}
      </div>
    </article>
  )
}

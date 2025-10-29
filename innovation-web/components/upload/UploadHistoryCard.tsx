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
      <div
        className="relative overflow-hidden h-[200px]"
        style={{
          background: `linear-gradient(to bottom right, ${colorScheme.from}, ${colorScheme.via}, ${colorScheme.to})`
        }}
      >
        {/* Abstract wave shapes */}
        <div className="absolute inset-0">
          <svg className="absolute w-full h-full" viewBox="0 0 300 200" preserveAspectRatio="none">
            <defs>
              <linearGradient id={`grad1-${upload.upload_id}`} x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style={{stopColor: colorScheme.grad1Start, stopOpacity: 1}} />
                <stop offset="100%" style={{stopColor: colorScheme.grad1End, stopOpacity: 1}} />
              </linearGradient>
              <linearGradient id={`grad2-${upload.upload_id}`} x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" style={{stopColor: colorScheme.grad2Start, stopOpacity: 0.8}} />
                <stop offset="100%" style={{stopColor: colorScheme.grad2End, stopOpacity: 0.6}} />
              </linearGradient>
            </defs>

            {/* Wave shapes */}
            <ellipse cx="250" cy="80" rx="120" ry="100" fill={`url(#grad1-${upload.upload_id})`} opacity="0.7" />
            <ellipse cx="80" cy="150" rx="100" ry="80" fill={`url(#grad2-${upload.upload_id})`} opacity="0.6" />
            <circle cx="200" cy="160" r="60" fill={colorScheme.circle} opacity="0.5" />
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
              {category}
            </div>
            <div className="flex items-center gap-1 text-xs font-bold text-black/60">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V9.99h7V2.95l8 3.98v7.06h-8z"/>
              </svg>
              <span className="uppercase tracking-wide">Document Analysis</span>
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
          {description}
        </p>
        <div className="mt-3 text-xs text-black/50 font-medium">
          {relativeTime}
        </div>
      </div>
    </article>
  )
}

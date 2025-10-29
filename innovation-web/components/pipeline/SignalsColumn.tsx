import { useMemo } from 'react'
import Image from 'next/image'
import { SignalIcon } from '../icons'

interface SignalsColumnProps {
  trendImage?: string
  trendTitle: string
  trendDescription?: string
  onClick?: () => void
  blobUrl?: string // Optional PDF URL for blurred preview background
}

// Color schemes for random assignment (same as UploadHistoryCard)
const COLOR_SCHEMES = [
  { from: '#FFB6C1', to: '#FF6B6B' },
  { from: '#A7C7E7', to: '#4682B4' },
  { from: '#DDA0DD', to: '#BA55D3' },
  { from: '#98FB98', to: '#3CB371' },
  { from: '#FFD700', to: '#FF8C00' },
  { from: '#F0E68C', to: '#BDB76B' },
]

// Extract category from title/filename
function extractCategory(title: string): string {
  const lowerTitle = title.toLowerCase()

  if (lowerTitle.includes('food') || lowerTitle.includes('beverage') || lowerTitle.includes('restaurant') ||
      lowerTitle.includes('culinary') || lowerTitle.includes('drink') || lowerTitle.includes('nutrition')) {
    return 'Food & Beverage'
  }
  if (lowerTitle.includes('tech') || lowerTitle.includes('digital') || lowerTitle.includes('software') ||
      lowerTitle.includes('ai') || lowerTitle.includes('automation') || lowerTitle.includes('data')) {
    return 'Technology'
  }
  if (lowerTitle.includes('health') || lowerTitle.includes('wellness') || lowerTitle.includes('medical') ||
      lowerTitle.includes('fitness') || lowerTitle.includes('pharma')) {
    return 'Health & Wellness'
  }
  if (lowerTitle.includes('retail') || lowerTitle.includes('commerce') || lowerTitle.includes('store') ||
      lowerTitle.includes('shop') || lowerTitle.includes('ecommerce')) {
    return 'Retail & Commerce'
  }
  if (lowerTitle.includes('finance') || lowerTitle.includes('bank') || lowerTitle.includes('fintech') ||
      lowerTitle.includes('invest') || lowerTitle.includes('payment')) {
    return 'Financial Services'
  }
  if (lowerTitle.includes('fashion') || lowerTitle.includes('apparel') || lowerTitle.includes('clothing') ||
      lowerTitle.includes('beauty') || lowerTitle.includes('cosmetic')) {
    return 'Fashion & Apparel'
  }
  if (lowerTitle.includes('energy') || lowerTitle.includes('sustainability') || lowerTitle.includes('renewable') ||
      lowerTitle.includes('green') || lowerTitle.includes('climate')) {
    return 'Energy & Sustainability'
  }
  if (lowerTitle.includes('auto') || lowerTitle.includes('vehicle') || lowerTitle.includes('car') ||
      lowerTitle.includes('mobility') || lowerTitle.includes('transport')) {
    return 'Automotive'
  }
  if (lowerTitle.includes('travel') || lowerTitle.includes('hospitality') || lowerTitle.includes('hotel') ||
      lowerTitle.includes('tourism') || lowerTitle.includes('airline')) {
    return 'Travel & Hospitality'
  }
  if (lowerTitle.includes('media') || lowerTitle.includes('entertainment') || lowerTitle.includes('content') ||
      lowerTitle.includes('streaming') || lowerTitle.includes('gaming')) {
    return 'Media & Entertainment'
  }
  if (lowerTitle.includes('education') || lowerTitle.includes('learning') || lowerTitle.includes('training') ||
      lowerTitle.includes('academic') || lowerTitle.includes('edtech')) {
    return 'Education & Learning'
  }

  return 'Innovation Research'
}

// Hash function for consistent color assignment
function hashString(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  return Math.abs(hash)
}

export const SignalsColumn: React.FC<SignalsColumnProps> = ({
  trendImage,
  trendTitle,
  onClick,
  blobUrl,
}) => {
  // Generate consistent color scheme and category based on title
  const { colorScheme, category } = useMemo(() => {
    const hash = hashString(trendTitle)
    const colorIndex = hash % COLOR_SCHEMES.length

    return {
      colorScheme: COLOR_SCHEMES[colorIndex],
      category: extractCategory(trendTitle),
    }
  }, [trendTitle])

  return (
    <div className="flex flex-col h-full flex-[0.7] min-w-[280px]">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <SignalIcon />
        <h3 className="text-lg font-semibold text-gray-900">Signals</h3>
      </div>

      {/* Signal Card - Matches mockup page 3 design */}
      <div
        className={`relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden h-[350px] flex flex-col ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
        onClick={onClick}
      >
        {/* Hero Image with overlay title */}
        <div className="relative w-full flex-1">
          {trendImage ? (
            <div className="relative w-full h-full">
              <Image
                src={trendImage}
                alt={trendTitle}
                fill
                className="object-cover"
              />
            </div>
          ) : (
            <div className="relative w-full h-full overflow-hidden">
              {/* Gradient background layer */}
              <div
                className="absolute inset-0 z-10"
                style={{
                  background: `linear-gradient(to bottom right, ${colorScheme.from}, ${colorScheme.to})`
                }}
              />

              {/* Blurred PDF preview layer (if available) */}
              {blobUrl && (
                <div className="absolute inset-0 z-0">
                  <iframe
                    src={`${blobUrl}#view=FitH`}
                    className="w-full h-full blur-3xl scale-110 opacity-30"
                    title="Document preview background"
                    style={{ pointerEvents: 'none' }}
                  />
                </div>
              )}
            </div>
          )}

          {/* Title overlay at bottom with category badge */}
          <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-4 z-20">
            <div className="mb-1.5">
              <span className="inline-block text-xs font-semibold text-gray-600 bg-gray-100 px-2 py-0.5 rounded">
                {category}
              </span>
            </div>
            <p className="text-sm text-gray-900 font-medium leading-relaxed">
              {trendTitle}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

'use client'

import { useRef, useEffect } from 'react'
import Image from 'next/image'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { DURATION, EASING_FUNCTION } from '@/lib/transitions'
import { getCardColorGradient } from '@/lib/card-colors'
import { SignalIcon, InsightsIcon, SparksIcon } from '@/components/icons'

export interface Spark {
  id: string
  title: string
  summary: string
  heroImageUrl?: string
  content: string
}

export interface CollapsedSidebarProps {
  sparks: Spark[]
  selectedId: string
  onSelectSpark: (id: string) => void
  /** Controls collapsed state animation (default: false = expanded) */
  isCollapsed?: boolean
  /** Callback when user clicks Signal or Insights icons to go back */
  onBackToColumns?: () => void
  /** Controls sticky positioning (default: true) */
  isSticky?: boolean
  /** Callback to toggle sticky state */
  onToggleSticky?: () => void
}

export default function CollapsedSidebar({
  sparks,
  selectedId,
  onSelectSpark,
  isCollapsed = false,
  onBackToColumns,
  isSticky = true,
  onToggleSticky,
}: CollapsedSidebarProps) {
  const selectedRef = useRef<HTMLDivElement>(null)
  const reducedMotion = useReducedMotion()

  useEffect(() => {
    // Auto-scroll to selected thumbnail
    selectedRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    })
  }, [selectedId])

  const duration = reducedMotion ? 0 : DURATION.SIDEBAR

  return (
    <div
      className="bg-gray-50 border-r border-gray-200 overflow-y-auto h-screen transition-all"
      style={{
        width: isCollapsed ? '240px' : '100%',
        position: isSticky ? 'sticky' : 'relative',
        top: isSticky ? '0' : 'auto',
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        transitionProperty: 'width, position, top'
      }}
    >
      {/* Header with 3 icons in a row + sticky toggle */}
      <div className="flex gap-1 p-2 border-b border-gray-200">
        <button
          onClick={onBackToColumns}
          className="flex-1 flex items-center justify-center h-8 opacity-40 hover:opacity-60 transition-opacity cursor-pointer"
          title="Back to Signals"
        >
          <SignalIcon />
        </button>
        <button
          onClick={onBackToColumns}
          className="flex-1 flex items-center justify-center h-8 opacity-40 hover:opacity-60 transition-opacity cursor-pointer"
          title="Back to Insights"
        >
          <InsightsIcon />
        </button>
        <div className="flex-1 flex items-center justify-center h-8">
          <SparksIcon />
        </div>
        <button
          onClick={onToggleSticky || (() => {})}
          className="flex items-center justify-center h-8 w-8 hover:bg-teal-50 rounded-full transition-all"
          title={isSticky ? 'Unstick sidebar (scroll with page)' : 'Stick sidebar (fixed position)'}
          aria-label={isSticky ? 'Unstick sidebar' : 'Stick sidebar'}
          data-testid="sticky-toggle"
        >
          {isSticky ? (
            // Locked icon
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="5" y="11" width="14" height="10" rx="2" stroke="#5B9A99" strokeWidth="2"/>
              <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#5B9A99" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="12" cy="16" r="1.5" fill="#5B9A99"/>
            </svg>
          ) : (
            // Unlocked icon
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <rect x="5" y="11" width="14" height="10" rx="2" stroke="#9CA3AF" strokeWidth="2"/>
              <path d="M8 11V7a4 4 0 0 1 8 0v3" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="12" cy="16" r="1.5" fill="#9CA3AF"/>
            </svg>
          )}
        </button>
      </div>

      {/* 3-column collapsed layout */}
      <div className="flex h-full">
        {/* Signal Column - Collapsed */}
        <div className="flex-1 flex flex-col gap-1.5 p-1.5 border-r border-gray-200 opacity-40">
          <div className="w-full aspect-square bg-white rounded flex items-center justify-center border border-gray-200">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <rect x="6" y="4" width="12" height="16" rx="2" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <div className="w-full aspect-square bg-white rounded flex items-center justify-center border border-gray-200">
            <span className="text-xl text-gray-600">+</span>
          </div>
        </div>

        {/* Insights Column - Collapsed */}
        <div className="flex-1 flex flex-col gap-1.5 p-1.5 border-r border-gray-200 opacity-40">
          <div className="w-full aspect-square bg-white rounded flex items-center justify-center border border-gray-200">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" strokeWidth="2"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
        </div>

        {/* Sparks Column - Active with thumbnails */}
        <div className="flex-1 flex flex-col gap-1.5 p-1.5">
          {sparks.map((spark, index) => {
            const gradientClass = getCardColorGradient(index + 1)

            return (
              <div
                key={spark.id}
                ref={spark.id === selectedId ? selectedRef : null}
                onClick={() => onSelectSpark(spark.id)}
                className={`
                  relative w-full aspect-square rounded overflow-hidden cursor-pointer
                  transition-all
                  hover:shadow-md
                  ${spark.id === selectedId ? 'ring-2 ring-[#5B9A99]' : 'ring-1 ring-gray-200'}
                `}
                style={{
                  transform: isCollapsed ? 'scale(0.98)' : 'scale(1)',
                  transitionDuration: `${duration}ms`,
                  transitionTimingFunction: EASING_FUNCTION
                }}
              >
                {spark.heroImageUrl ? (
                  <Image
                    src={spark.heroImageUrl}
                    alt={spark.title}
                    fill
                    className="object-cover"
                  />
                ) : (
                  <div className={`w-full h-full bg-gradient-to-br ${gradientClass} flex items-center justify-center`}>
                    <span className="text-white/30 text-xl font-bold">{index + 1}</span>
                  </div>
                )}
                <div className="absolute top-1 left-1 w-5 h-5 bg-white rounded-full flex items-center justify-center text-xs font-bold shadow-sm">
                  {index + 1}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

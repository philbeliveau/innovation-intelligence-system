'use client'

import { useRef, useEffect } from 'react'
import Image from 'next/image'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { DURATION, EASING_FUNCTION } from '@/lib/transitions'

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
}

export default function CollapsedSidebar({
  sparks,
  selectedId,
  onSelectSpark,
  isCollapsed = false,
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
      className="bg-white border-r border-gray-200 overflow-y-auto h-full transition-all"
      style={{
        width: isCollapsed ? '120px' : '100%',
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        transitionProperty: 'width'
      }}
    >
      <div className="flex flex-col gap-2 p-2">
        {sparks.map((spark, index) => (
          <div
            key={spark.id}
            ref={spark.id === selectedId ? selectedRef : null}
            onClick={() => onSelectSpark(spark.id)}
            className={`
              relative w-20 h-20 rounded-lg overflow-hidden cursor-pointer
              transition-all
              hover:shadow-md
              ${spark.id === selectedId ? 'ring-2 ring-[#5B9A99]' : 'ring-1 ring-gray-200'}
            `}
            style={{
              transform: isCollapsed ? 'scale(0.9)' : 'scale(1)',
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
              <div className="w-full h-full bg-gray-200" />
            )}
            <div className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full flex items-center justify-center text-xs font-bold shadow-sm">
              {index + 1}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

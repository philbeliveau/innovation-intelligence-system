/**
 * SkeletonBox Component
 * Loading placeholder with shimmer animation
 * Prevents layout shift when real components load
 */

import React from 'react'

export interface SkeletonBoxProps {
  width?: string
  height?: string
  className?: string
}

export default function SkeletonBox({
  width = '100%',
  height = '400px',
  className = '',
}: SkeletonBoxProps) {
  return (
    <div
      className={`
        relative overflow-hidden
        bg-gray-200 rounded-lg
        ${className}
      `}
      style={{ width, height }}
      aria-busy="true"
      aria-label="Loading..."
    >
      {/* Shimmer animation overlay */}
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/40 to-transparent" />
    </div>
  )
}

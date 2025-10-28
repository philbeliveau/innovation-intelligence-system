/**
 * BOIBadge Component
 * Reusable "Board of Ideators" branding badge
 * Used across pipeline visualization components
 */

import React from 'react'

export interface BOIBadgeProps {
  size?: 'small' | 'medium' | 'large'
  className?: string
}

export default function BOIBadge({ size = 'medium', className = '' }: BOIBadgeProps) {
  const sizeClasses = {
    small: 'w-8 h-8 text-xs',
    medium: 'w-12 h-12 text-sm',
    large: 'w-16 h-16 text-base',
  }

  return (
    <div
      className={`
        absolute top-4 left-4
        rounded-full bg-[#5B9A99]
        flex items-center justify-center
        font-bold text-white
        ${sizeClasses[size]}
        ${className}
      `}
      aria-label="Board of Ideators"
    >
      BOI
    </div>
  )
}

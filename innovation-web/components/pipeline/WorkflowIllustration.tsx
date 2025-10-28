/**
 * WorkflowIllustration Component
 * Displays visual representation of the pipeline workflow
 * Shows what Stage 1 does with optional breathing animation
 */

'use client'

import React, { useState } from 'react'
import BOIBadge from './BOIBadge'

export interface WorkflowIllustrationProps {
  imageUrl?: string
  showAnimation?: boolean
}

// Fallback SVG illustration when no image provided
const FallbackIllustrationSVG = ({ showAnimation }: { showAnimation: boolean }) => (
  <svg
    viewBox="0 0 400 300"
    className={`w-full h-64 mx-auto ${showAnimation ? 'breathe-animation' : ''}`}
    aria-hidden="true"
  >
    {/* Document icon */}
    <g transform="translate(50, 50)">
      <rect
        x="0"
        y="0"
        width="80"
        height="100"
        fill="white"
        stroke="#5B9A99"
        strokeWidth="2"
        rx="4"
      />
      <line x1="10" y1="20" x2="70" y2="20" stroke="#5B9A99" strokeWidth="2" />
      <line x1="10" y1="35" x2="70" y2="35" stroke="#5B9A99" strokeWidth="2" />
      <line x1="10" y1="50" x2="70" y2="50" stroke="#5B9A99" strokeWidth="2" />
      <line x1="10" y1="65" x2="50" y2="65" stroke="#5B9A99" strokeWidth="2" />
    </g>

    {/* Arrow */}
    <g transform="translate(140, 90)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="#5B9A99" strokeWidth="3" />
      <polygon points="40,0 30,-6 30,6" fill="#5B9A99" />
    </g>

    {/* Processing brain/gear icon */}
    <g transform="translate(200, 60)">
      <circle cx="20" cy="30" r="25" fill="none" stroke="#5B9A99" strokeWidth="2" />
      <circle cx="20" cy="30" r="15" fill="#5B9A99" opacity="0.2" />

      {/* Gear teeth */}
      <circle cx="20" cy="5" r="3" fill="#5B9A99" />
      <circle cx="35" cy="18" r="3" fill="#5B9A99" />
      <circle cx="35" cy="42" r="3" fill="#5B9A99" />
      <circle cx="20" cy="55" r="3" fill="#5B9A99" />
      <circle cx="5" cy="42" r="3" fill="#5B9A99" />
      <circle cx="5" cy="18" r="3" fill="#5B9A99" />
    </g>

    {/* Arrow */}
    <g transform="translate(255, 90)">
      <line x1="0" y1="0" x2="40" y2="0" stroke="#5B9A99" strokeWidth="3" />
      <polygon points="40,0 30,-6 30,6" fill="#5B9A99" />
    </g>

    {/* Output insights icon */}
    <g transform="translate(305, 50)">
      <rect
        x="0"
        y="0"
        width="80"
        height="100"
        fill="white"
        stroke="#5B9A99"
        strokeWidth="2"
        rx="4"
      />

      {/* Lightbulb */}
      <circle cx="40" cy="40" r="12" fill="#5B9A99" opacity="0.3" />
      <rect x="36" y="52" width="8" height="6" fill="#5B9A99" opacity="0.3" rx="1" />

      {/* Sparkle marks */}
      <text x="20" y="75" fontSize="20" fill="#5B9A99">✨</text>
      <text x="52" y="75" fontSize="20" fill="#5B9A99">✨</text>
    </g>
  </svg>
)

export default function WorkflowIllustration({
  imageUrl,
  showAnimation = true,
}: WorkflowIllustrationProps) {
  const [imageError, setImageError] = useState(false)

  return (
    <div className="relative h-full flex flex-col items-center justify-center">
      <BOIBadge size="medium" />

      <div className="text-center space-y-6 w-full px-4">
        {/* Illustration - image or SVG fallback */}
        {imageUrl && !imageError ? (
          <img
            src={imageUrl}
            alt="Pipeline workflow illustration"
            className={`w-full max-w-md mx-auto ${showAnimation ? 'breathe-animation' : ''}`}
            onError={() => setImageError(true)}
            loading="lazy"
          />
        ) : (
          <FallbackIllustrationSVG showAnimation={showAnimation} />
        )}

        {/* Description text */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-900">
            Understanding the core transferable pattern
          </h3>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Stage 1 analyzes your document to extract the fundamental mechanisms and patterns that
            can be adapted to new contexts.
          </p>
        </div>

        {/* Stage flow indicators */}
        <div className="flex items-center justify-center gap-2 text-sm text-gray-500 flex-wrap">
          <span className="px-3 py-1 bg-[#5B9A99] bg-opacity-10 rounded-full">Extract</span>
          <span>→</span>
          <span className="px-3 py-1 bg-gray-100 rounded-full">Amplify</span>
          <span>→</span>
          <span className="px-3 py-1 bg-gray-100 rounded-full">Translate</span>
          <span>→</span>
          <span className="px-3 py-1 bg-gray-100 rounded-full">Contextualize</span>
          <span>→</span>
          <span className="px-3 py-1 bg-gray-100 rounded-full">Generate</span>
        </div>
      </div>
    </div>
  )
}

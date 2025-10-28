/**
 * ExtractionAnimation Component
 * Animated beaker visualization for Stage 1 extraction process
 * Displays bubbling animation while processing, error state if failed
 */

'use client'

import React from 'react'
import BOIBadge from './BOIBadge'

export interface ExtractionAnimationProps {
  status: 'running' | 'error'
  elapsedTime?: number
}

const BeakerSVG = ({ isAnimating }: { isAnimating: boolean }) => (
  <svg
    viewBox="0 0 200 300"
    className="w-32 h-48 mx-auto"
    aria-hidden="true"
  >
    {/* Beaker body */}
    <path
      d="M 60 50 L 60 200 Q 100 250 140 200 L 140 50 Z"
      fill="none"
      stroke="#5B9A99"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    />

    {/* Beaker neck */}
    <rect
      x="85"
      y="30"
      width="30"
      height="20"
      fill="none"
      stroke="#5B9A99"
      strokeWidth="3"
      rx="2"
    />

    {/* Liquid fill */}
    <path
      d="M 65 150 L 65 195 Q 100 235 135 195 L 135 150 Z"
      fill="#5B9A99"
      opacity="0.3"
    />

    {/* Measurement lines */}
    <line x1="145" y1="100" x2="155" y2="100" stroke="#5B9A99" strokeWidth="1.5" />
    <line x1="145" y1="150" x2="155" y2="150" stroke="#5B9A99" strokeWidth="1.5" />
    <line x1="145" y1="200" x2="155" y2="200" stroke="#5B9A99" strokeWidth="1.5" />

    {/* Animated bubbles - only when running */}
    {isAnimating && (
      <>
        <circle
          cx="90"
          cy="180"
          r="4"
          fill="#5B9A99"
          className="bubble-animation"
          style={{ animationDelay: '0s' }}
        />
        <circle
          cx="110"
          cy="190"
          r="3"
          fill="#5B9A99"
          className="bubble-animation"
          style={{ animationDelay: '0.5s' }}
        />
        <circle
          cx="100"
          cy="170"
          r="3.5"
          fill="#5B9A99"
          className="bubble-animation"
          style={{ animationDelay: '1s' }}
        />
        <circle
          cx="85"
          cy="195"
          r="2.5"
          fill="#5B9A99"
          className="bubble-animation"
          style={{ animationDelay: '1.5s' }}
        />
        <circle
          cx="115"
          cy="175"
          r="3"
          fill="#5B9A99"
          className="bubble-animation"
          style={{ animationDelay: '2s' }}
        />
      </>
    )}
  </svg>
)

export default function ExtractionAnimation({ status, elapsedTime }: ExtractionAnimationProps) {
  const isRunning = status === 'running'
  const isError = status === 'error'

  return (
    <div className="relative h-full flex flex-col items-center justify-center">
      <BOIBadge size="medium" />

      {/* Error overlay */}
      {isError && (
        <div className="absolute inset-0 bg-red-500 opacity-20 rounded-lg pointer-events-none" />
      )}

      {/* Main content */}
      <div className="text-center space-y-6">
        {/* Beaker illustration or error icon */}
        {isError ? (
          <div className="text-6xl mb-4" aria-label="Error">
            ⚠️
          </div>
        ) : (
          <BeakerSVG isAnimating={isRunning} />
        )}

        {/* Status text */}
        <div className="space-y-2">
          <h3 className="text-xl font-semibold text-gray-900">
            {isError ? 'Extraction encountered an error' : 'Extracting transferable insights from your document'}
          </h3>

          {isRunning && elapsedTime && (
            <p className="text-sm text-gray-500">
              Elapsed time: {Math.floor(elapsedTime / 1000)}s
            </p>
          )}
        </div>

        {/* Processing indicator for running state */}
        {isRunning && (
          <div className="flex items-center justify-center gap-2 mt-4">
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-teal-100 border-t-[#5B9A99]" />
            <span className="text-sm text-gray-500">Processing...</span>
          </div>
        )}
      </div>
    </div>
  )
}

'use client'

import { useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import Image from 'next/image'
import { ArrowLeft, ChevronUp, ChevronDown } from 'lucide-react'
import { Spark } from './CollapsedSidebar'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { useWillChange } from '@/hooks/useWillChange'
import { DURATION, EASING_FUNCTION } from '@/lib/transitions'
import { getCardColorGradient } from '@/lib/card-colors'

export interface ExpandedSparkDetailProps {
  spark: Spark
  onBack: () => void
  // Mobile navigation props
  currentIndex?: number
  totalSparks?: number
  onPrev?: () => void
  onNext?: () => void
  /** Callback fired when entrance animation completes */
  onAnimationComplete?: () => void
  /** Card number for gradient color (1-based index) */
  cardNumber?: number
}

/**
 * Mobile navigation bar for spark navigation
 */
function MobileNavBar({
  currentIndex,
  total,
  onPrev,
  onNext,
  onBack,
}: {
  currentIndex: number
  total: number
  onPrev: () => void
  onNext: () => void
  onBack: () => void
}) {
  return (
    <div className="md:hidden sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="text-[#5B9A99] hover:text-[#4A7F7E] transition-colors"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div className="flex items-center gap-4">
          <button
            onClick={onPrev}
            disabled={currentIndex === 0}
            className="disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronUp className="w-6 h-6" />
          </button>
          <span className="text-sm font-medium">
            {currentIndex + 1} of {total}
          </span>
          <button
            onClick={onNext}
            disabled={currentIndex === total - 1}
            className="disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <ChevronDown className="w-6 h-6" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default function ExpandedSparkDetail({
  spark,
  onBack,
  currentIndex,
  totalSparks,
  onPrev,
  onNext,
  onAnimationComplete,
  cardNumber,
}: ExpandedSparkDetailProps) {
  const hasMobileNav = currentIndex !== undefined && totalSparks !== undefined && onPrev && onNext
  const reducedMotion = useReducedMotion()
  const containerRef = useWillChange(true) // Animating on mount

  const duration = reducedMotion ? 0 : DURATION.SIDEBAR

  // Get gradient class for header image (use currentIndex + 1 if cardNumber not provided)
  const displayNumber = cardNumber ?? (currentIndex !== undefined ? currentIndex + 1 : 1)
  const gradientClass = getCardColorGradient(displayNumber)

  // Trigger animation complete callback
  useEffect(() => {
    if (onAnimationComplete) {
      const timeout = setTimeout(onAnimationComplete, duration)
      return () => clearTimeout(timeout)
    }
  }, [duration, onAnimationComplete])

  // Focus management for accessibility
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.focus()
    }
  }, [spark.id, containerRef])

  return (
    <div
      ref={containerRef as React.RefObject<HTMLDivElement>}
      className="flex-1 overflow-y-auto h-full bg-white transition-all"
      style={{
        opacity: 1,
        transform: 'translateX(0)',
        transitionDuration: `${duration}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        transitionProperty: 'opacity, transform'
      }}
      tabIndex={-1}
      aria-label={`Spark detail: ${spark.title}`}
    >
      {/* Mobile Navigation (if props provided) */}
      {hasMobileNav && (
        <MobileNavBar
          currentIndex={currentIndex}
          total={totalSparks}
          onPrev={onPrev}
          onNext={onNext}
          onBack={onBack}
        />
      )}

      {/* Hero Image - Full width at top */}
      <div className="relative w-full h-48">
        {spark.heroImageUrl ? (
          <Image
            src={spark.heroImageUrl}
            alt={spark.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${gradientClass} flex items-center justify-center`}>
            <span className="text-white/20 text-6xl font-bold">{displayNumber}</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="px-6 md:px-12 py-8 max-w-4xl mx-auto">

        {/* Markdown Content */}
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
          components={{
            h1: ({ ...props }) => (
              <h1 className="text-4xl font-bold mb-4 text-gray-900" {...props} />
            ),
            h2: ({ ...props }) => (
              <h2 className="text-3xl font-semibold mb-3 mt-8 text-gray-900" {...props} />
            ),
            h3: ({ ...props }) => (
              <h3 className="text-2xl font-semibold mb-2 mt-6 text-gray-900" {...props} />
            ),
            h4: ({ ...props }) => (
              <h4 className="text-xl font-semibold mb-2 mt-4 text-gray-900" {...props} />
            ),
            h5: ({ ...props }) => (
              <h5 className="text-lg font-semibold mb-2 mt-3 text-gray-900" {...props} />
            ),
            h6: ({ ...props }) => (
              <h6 className="text-base font-semibold mb-2 mt-2 text-gray-900" {...props} />
            ),
            p: ({ ...props }) => (
              <p className="mb-4 leading-7 text-gray-700" {...props} />
            ),
            a: ({ ...props }) => (
              <a
                className="text-[#5B9A99] underline hover:text-[#4A7F7E] transition-colors"
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              />
            ),
            img: ({ ...props }: React.ImgHTMLAttributes<HTMLImageElement>) => {
              const src = typeof props.src === 'string' ? props.src : ''
              const alt = typeof props.alt === 'string' ? props.alt : ''
              return (
                <div className="my-4 rounded-lg overflow-hidden">
                  <Image
                    src={src}
                    alt={alt}
                    width={800}
                    height={600}
                    className="rounded-lg"
                  />
                </div>
              )
            },
            code: ({ inline, ...props }: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) =>
              inline ? (
                <code
                  className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono"
                  {...props}
                />
              ) : (
                <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
                  <code className="font-mono text-sm" {...props} />
                </pre>
              ),
            ul: ({ ...props }) => (
              <ul className="list-disc list-inside mb-4 space-y-1" {...props} />
            ),
            ol: ({ ...props }) => (
              <ol className="list-decimal list-inside mb-4 space-y-1" {...props} />
            ),
            li: ({ ...props }) => (
              <li className="text-gray-700 leading-7" {...props} />
            ),
            blockquote: ({ ...props }) => (
              <blockquote
                className="border-l-4 border-[#5B9A99] pl-4 italic my-4 text-gray-600"
                {...props}
              />
            ),
            table: ({ ...props }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-gray-300" {...props} />
              </div>
            ),
            th: ({ ...props }) => (
              <th className="border border-gray-300 px-4 py-2 bg-gray-100 font-semibold" {...props} />
            ),
            td: ({ ...props }) => (
              <td className="border border-gray-300 px-4 py-2" {...props} />
            ),
          }}
        >
          {spark.content}
        </ReactMarkdown>
      </div>
    </div>
  )
}

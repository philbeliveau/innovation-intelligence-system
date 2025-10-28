'use client'

import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import Image from 'next/image'
import { ArrowLeft, ChevronUp, ChevronDown } from 'lucide-react'
import { Spark } from './CollapsedSidebar'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { useWillChange } from '@/hooks/useWillChange'
import { DURATION, EASING_FUNCTION } from '@/lib/transitions'

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
}: ExpandedSparkDetailProps) {
  const hasMobileNav = currentIndex !== undefined && totalSparks !== undefined && onPrev && onNext
  const reducedMotion = useReducedMotion()
  const containerRef = useWillChange(true) // Animating on mount

  const duration = reducedMotion ? 0 : DURATION.SIDEBAR

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
  }, [spark.id])

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

      {/* Desktop Sticky Header with Back Button */}
      <div className="hidden md:block sticky top-0 z-10 bg-white border-b border-gray-200 px-12 py-4">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-[#5B9A99] hover:text-[#4A7F7E] transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span className="font-medium">Back to Grid</span>
        </button>
      </div>

      {/* Content */}
      <div className="px-6 md:px-12 py-8 max-w-4xl mx-auto">
        {/* Hero Image */}
        {spark.heroImageUrl && (
          <div className="relative aspect-video mb-8 rounded-lg overflow-hidden">
            <Image
              src={spark.heroImageUrl}
              alt={spark.title}
              fill
              className="object-cover"
            />
          </div>
        )}

        {/* Markdown Content */}
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
          components={{
            h1: ({ node, ...props }) => (
              <h1 className="text-4xl font-bold mb-4 text-gray-900" {...props} />
            ),
            h2: ({ node, ...props }) => (
              <h2 className="text-3xl font-semibold mb-3 mt-8 text-gray-900" {...props} />
            ),
            h3: ({ node, ...props }) => (
              <h3 className="text-2xl font-semibold mb-2 mt-6 text-gray-900" {...props} />
            ),
            h4: ({ node, ...props }) => (
              <h4 className="text-xl font-semibold mb-2 mt-4 text-gray-900" {...props} />
            ),
            h5: ({ node, ...props }) => (
              <h5 className="text-lg font-semibold mb-2 mt-3 text-gray-900" {...props} />
            ),
            h6: ({ node, ...props }) => (
              <h6 className="text-base font-semibold mb-2 mt-2 text-gray-900" {...props} />
            ),
            p: ({ node, ...props }) => (
              <p className="mb-4 leading-7 text-gray-700" {...props} />
            ),
            a: ({ node, ...props }) => (
              <a
                className="text-[#5B9A99] underline hover:text-[#4A7F7E] transition-colors"
                target="_blank"
                rel="noopener noreferrer"
                {...props}
              />
            ),
            img: ({ node, ...props }) => {
              const src = props.src || ''
              const alt = props.alt || ''
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
            code: ({ inline, ...props }: { inline?: boolean; [key: string]: unknown }) =>
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
            ul: ({ node, ...props }) => (
              <ul className="list-disc list-inside mb-4 space-y-1" {...props} />
            ),
            ol: ({ node, ...props }) => (
              <ol className="list-decimal list-inside mb-4 space-y-1" {...props} />
            ),
            li: ({ node, ...props }) => (
              <li className="text-gray-700 leading-7" {...props} />
            ),
            blockquote: ({ node, ...props }) => (
              <blockquote
                className="border-l-4 border-[#5B9A99] pl-4 italic my-4 text-gray-600"
                {...props}
              />
            ),
            table: ({ node, ...props }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border-collapse border border-gray-300" {...props} />
              </div>
            ),
            th: ({ node, ...props }) => (
              <th className="border border-gray-300 px-4 py-2 bg-gray-100 font-semibold" {...props} />
            ),
            td: ({ node, ...props }) => (
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

'use client'

import { useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './OpportunityModal.css'

interface OpportunityModalProps {
  isOpen: boolean
  onClose: () => void
  number: number
  title: string
  markdown: string
  innovationType: string
}

export default function OpportunityModal({
  isOpen,
  onClose,
  number,
  title,
  markdown,
  innovationType,
}: OpportunityModalProps) {
  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  // Parse markdown frontmatter to extract content
  const parseFrontmatter = (md: string) => {
    const match = md.match(/^---\n([\s\S]*?)\n---/)
    if (!match) return md
    return md.slice(match[0].length).trim()
  }

  const content = parseFrontmatter(markdown)

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-0 sm:p-4"
      onClick={onClose}
    >
      <div
        className="relative w-full h-full sm:h-auto sm:max-w-3xl bg-white border-0 sm:border-[3px] md:border-[5px] border-black shadow-none sm:shadow-[8px_8px_0_#000] md:shadow-[12px_12px_0_#000] sm:max-h-[90vh] overflow-hidden sm:rounded-none"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header - Full screen on mobile, compact on desktop */}
        <div className="border-b-[3px] sm:border-b-[5px] border-black bg-gradient-to-r from-amber-200 to-amber-400 p-4 sm:p-6">
          <div className="flex items-start justify-between gap-2 sm:gap-4">
            <div className="flex-1">
              <div className="mb-1 sm:mb-2 text-2xl sm:text-4xl font-black text-black/20">#{number}</div>
              <h2 className="text-lg sm:text-2xl font-black uppercase leading-tight text-black mb-2 sm:mb-3">
                {title}
              </h2>
              <span className="inline-block border-2 border-black bg-orange-500 px-2 sm:px-3 py-0.5 sm:py-1 text-[10px] sm:text-xs font-bold text-white uppercase shadow-[2px_2px_0_#000]">
                {innovationType}
              </span>
            </div>
            <button
              className="flex-shrink-0 h-9 w-9 sm:h-10 sm:w-10 bg-black text-white hover:bg-gray-800 transition-colors border-2 border-black font-bold text-lg sm:text-xl"
              onClick={onClose}
              aria-label="Close modal"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content - Notion-style beautiful formatting */}
        <div className="overflow-y-auto p-6 sm:p-8 bg-white" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          <div className="max-w-3xl mx-auto">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Prevent dangerous elements (XSS protection)
                script: () => null,
                iframe: () => null,
                object: () => null,
                embed: () => null,

                // Notion-style headings with clean hierarchy
                h1: ({ ...props }) => (
                  <h1
                    className="text-3xl sm:text-4xl font-bold mb-4 mt-8 text-black leading-tight tracking-tight first:mt-0"
                    {...props}
                  />
                ),
                h2: ({ ...props }) => (
                  <h2
                    className="text-2xl sm:text-3xl font-bold mb-3 mt-6 text-black leading-tight tracking-tight"
                    {...props}
                  />
                ),
                h3: ({ ...props }) => (
                  <h3
                    className="text-xl sm:text-2xl font-semibold mb-2 mt-5 text-black leading-snug"
                    {...props}
                  />
                ),
                h4: ({ ...props }) => (
                  <h4
                    className="text-lg sm:text-xl font-semibold mb-2 mt-4 text-gray-900"
                    {...props}
                  />
                ),

                // Notion-style paragraphs with generous spacing
                p: ({ ...props }) => (
                  <p
                    className="text-base sm:text-lg leading-relaxed mb-4 text-gray-800"
                    {...props}
                  />
                ),

                // Clean, readable lists
                ul: ({ ...props }) => (
                  <ul
                    className="space-y-2 mb-6 ml-6"
                    {...props}
                  />
                ),
                ol: ({ ...props }) => (
                  <ol
                    className="space-y-2 mb-6 ml-6 list-decimal"
                    {...props}
                  />
                ),
                li: ({ children, ...props }) => (
                  <li
                    className="text-base sm:text-lg leading-relaxed text-gray-800 pl-2"
                    {...props}
                  >
                    <span className="inline-flex items-start">
                      <span className="mr-2 text-black font-bold">•</span>
                      <span className="flex-1">{children}</span>
                    </span>
                  </li>
                ),

                // Styled links
                a: ({ ...props }) => (
                  <a
                    className="text-blue-600 hover:text-blue-700 underline decoration-blue-300 hover:decoration-blue-500 transition-colors"
                    {...props}
                  />
                ),

                // Bold text - Notion style
                strong: ({ ...props }) => (
                  <strong
                    className="font-semibold text-black"
                    {...props}
                  />
                ),

                // Inline code - Notion style
                code: ({ node, inline, className, ...props }: React.HTMLAttributes<HTMLElement> & { node?: unknown; inline?: boolean }) => {
                  if (inline) {
                    return (
                      <code
                        className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded font-mono text-sm"
                        {...props}
                      />
                    )
                  }
                  return (
                    <code
                      className="block bg-gray-50 border border-gray-200 p-4 rounded-lg font-mono text-sm overflow-x-auto my-4"
                      {...props}
                    />
                  )
                },

                // Code blocks - Notion style
                pre: ({ ...props }) => (
                  <pre
                    className="bg-gray-50 border border-gray-200 p-4 rounded-lg overflow-x-auto my-4"
                    {...props}
                  />
                ),

                // Blockquotes - Notion callout style
                blockquote: ({ ...props }) => (
                  <blockquote
                    className="border-l-4 border-amber-400 bg-amber-50 px-4 py-3 my-4 rounded-r"
                    {...props}
                  />
                ),

                // Tables - Clean Notion style
                table: ({ ...props }) => (
                  <div className="overflow-x-auto my-6">
                    <table
                      className="w-full border-collapse"
                      {...props}
                    />
                  </div>
                ),
                thead: ({ ...props }) => (
                  <thead
                    className="bg-gray-50 border-b-2 border-gray-200"
                    {...props}
                  />
                ),
                th: ({ ...props }) => (
                  <th
                    className="px-4 py-3 text-left text-sm font-semibold text-gray-900"
                    {...props}
                  />
                ),
                td: ({ ...props }) => (
                  <td
                    className="px-4 py-3 text-base text-gray-800 border-b border-gray-100"
                    {...props}
                  />
                ),

                // Horizontal rule - Notion style divider
                hr: ({ ...props }) => (
                  <hr
                    className="my-8 border-0 h-px bg-gray-200"
                    {...props}
                  />
                ),
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        </div>

        {/* Footer - Responsive button sizing */}
        <div className="border-t-[3px] sm:border-t-[5px] border-black bg-white p-3 sm:p-4">
          <button
            className="w-full bg-black text-white py-2.5 sm:py-3 px-4 sm:px-6 font-black uppercase text-base sm:text-lg hover:bg-gray-800 transition-colors shadow-[4px_4px_0_rgba(0,0,0,0.2)] active:shadow-[2px_2px_0_rgba(0,0,0,0.2)] active:translate-x-[2px] active:translate-y-[2px] min-h-[44px]"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

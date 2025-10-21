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

        {/* Content - Full screen scrollable on mobile */}
        <div className="overflow-y-auto p-4 sm:p-6" style={{ maxHeight: 'calc(100vh - 180px)', maxHeight: 'calc(90vh - 200px)' }}>
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Prevent dangerous elements (XSS protection)
              script: () => null,
              iframe: () => null,
              object: () => null,
              embed: () => null,
              // Style headings - Responsive sizing
              h1: ({ ...props }) => <h1 className="text-2xl sm:text-3xl font-black uppercase mb-3 sm:mb-4 mt-4 sm:mt-6 text-black border-b-4 border-black pb-2" {...props} />,
              h2: ({ ...props }) => <h2 className="text-xl sm:text-2xl font-black uppercase mb-2 sm:mb-3 mt-4 sm:mt-5 text-black" {...props} />,
              h3: ({ ...props }) => <h3 className="text-lg sm:text-xl font-bold uppercase mb-2 mt-3 sm:mt-4 text-black" {...props} />,
              h4: ({ ...props }) => <h4 className="text-base sm:text-lg font-bold mb-2 mt-2 sm:mt-3 text-black" {...props} />,
              // Style paragraphs
              p: ({ ...props }) => <p className="text-sm sm:text-base leading-relaxed mb-3 sm:mb-4 text-black" {...props} />,
              // Style lists
              ul: ({ ...props }) => <ul className="list-none space-y-2 mb-4 ml-0" {...props} />,
              ol: ({ ...props }) => <ol className="list-decimal space-y-2 mb-4 ml-6" {...props} />,
              li: ({ ...props }) => <li className="text-base leading-relaxed text-black before:content-['▸'] before:mr-2 before:font-bold" {...props} />,
              // Style links
              a: ({ ...props }) => <a className="text-orange-600 font-bold underline hover:text-orange-800" {...props} />,
              // Style strong/bold
              strong: ({ ...props }) => <strong className="font-black text-black" {...props} />,
              // Style code
              code: ({ ...props }) => <code className="bg-gray-100 border-2 border-black px-2 py-0.5 font-mono text-sm" {...props} />,
              // Style blockquote
              blockquote: ({ ...props }) => <blockquote className="border-l-4 border-black bg-amber-50 pl-4 py-2 italic my-4" {...props} />,
            }}
          >
            {content}
          </ReactMarkdown>
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

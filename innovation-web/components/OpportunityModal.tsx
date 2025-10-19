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
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-content">
            <div className="modal-number">#{number}</div>
            <div className="modal-title-section">
              <h2 className="modal-title">{title}</h2>
              <span className="modal-badge">{innovationType}</span>
            </div>
          </div>
          <button className="modal-close" onClick={onClose} aria-label="Close modal">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="modal-content">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Prevent dangerous elements (XSS protection)
              script: () => null,
              iframe: () => null,
              object: () => null,
              embed: () => null,
              // Style headings
              h1: ({ ...props }) => <h1 className="modal-h1" {...props} />,
              h2: ({ ...props }) => <h2 className="modal-h2" {...props} />,
              h3: ({ ...props }) => <h3 className="modal-h3" {...props} />,
              h4: ({ ...props }) => <h4 className="modal-h4" {...props} />,
              // Style paragraphs
              p: ({ ...props }) => <p className="modal-p" {...props} />,
              // Style lists
              ul: ({ ...props }) => <ul className="modal-ul" {...props} />,
              ol: ({ ...props }) => <ol className="modal-ol" {...props} />,
              li: ({ ...props }) => <li className="modal-li" {...props} />,
              // Style links
              a: ({ ...props }) => <a className="modal-a" {...props} />,
              // Style strong/bold
              strong: ({ ...props }) => <strong className="modal-strong" {...props} />,
              // Style code
              code: ({ ...props }) => <code className="modal-code" {...props} />,
              // Style blockquote
              blockquote: ({ ...props }) => <blockquote className="modal-blockquote" {...props} />,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button className="modal-close-button" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

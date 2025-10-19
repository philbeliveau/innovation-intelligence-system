'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './OpportunityCard.css'

interface OpportunityCardProps {
  number: number
  title: string
  markdown: string
}

export default function OpportunityCard({ number, title, markdown }: OpportunityCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  // Parse markdown frontmatter to extract metadata
  const parseFrontmatter = (md: string) => {
    const match = md.match(/^---\n([\s\S]*?)\n---/)
    if (!match) return { content: md, tags: '' }

    const frontmatter = match[1]
    const content = md.slice(match[0].length).trim()

    // Extract tags
    const tagsMatch = frontmatter.match(/tags:\s*(.+)/)
    const tags = tagsMatch ? tagsMatch[1] : ''

    return { content, tags }
  }

  const { content, tags } = parseFrontmatter(markdown)

  // Extract first paragraph from description as subtitle
  const descriptionRegex = /## Description\n\n([\s\S]*?)(?:\n\n|$)/
  const descriptionMatch = content.match(descriptionRegex)
  const subtitle = descriptionMatch
    ? descriptionMatch[1].split('.')[0] + '.'
    : 'Innovation opportunity for brand growth'

  // Get innovation type from tags
  const innovationType = tags.split(',')[0]?.trim() || 'innovation'

  return (
    <div
      className="card"
      onClick={() => setIsExpanded(!isExpanded)}
      style={{ width: isExpanded ? '500px' : '270px', minHeight: isExpanded ? '450px' : 'auto' }}
    >
      <div className="card__wrapper">
        <div className="card__title">#{number}</div>
        <div className="card__icon">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <g strokeWidth="0" id="SVGRepo_bgCarrier"></g>
            <g strokeLinejoin="round" strokeLinecap="round" id="SVGRepo_tracerCarrier"></g>
            <g id="SVGRepo_iconCarrier">
              <path
                fill="currentColor"
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"
              ></path>
            </g>
          </svg>
        </div>
      </div>

      <div className="card__title" style={{ fontSize: '18px', marginTop: '10px' }}>
        {title}
      </div>

      <div className="card__subtitle" style={{ fontSize: '14px', lineHeight: '1.4' }}>
        {subtitle}
      </div>

      {/* Innovation Type Badge */}
      <div style={{ marginTop: '10px' }}>
        <span
          style={{
            padding: '4px 12px',
            backgroundColor: 'var(--accent-color)',
            color: 'var(--bg-color)',
            fontSize: '12px',
            fontWeight: '600',
            borderRadius: '12px',
            textTransform: 'capitalize',
          }}
        >
          {innovationType}
        </span>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div
          style={{
            marginTop: '15px',
            maxHeight: '300px',
            overflowY: 'auto',
            color: 'var(--main-color)',
            fontSize: '14px',
          }}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Prevent dangerous elements (XSS protection)
              script: () => null,
              iframe: () => null,
              object: () => null,
              embed: () => null,
              // Style headings
              h1: ({ ...props }) => (
                <h1 style={{ fontSize: '16px', fontWeight: 'bold', marginTop: '12px', marginBottom: '8px', color: 'var(--main-color)' }} {...props} />
              ),
              h2: ({ ...props }) => (
                <h2 style={{ fontSize: '15px', fontWeight: '600', marginTop: '12px', marginBottom: '6px', color: 'var(--main-color)' }} {...props} />
              ),
              h3: ({ ...props }) => (
                <h3 style={{ fontSize: '14px', fontWeight: '600', marginTop: '8px', marginBottom: '4px', color: 'var(--sub-color)' }} {...props} />
              ),
              // Style paragraphs
              p: ({ ...props }) => (
                <p style={{ marginBottom: '8px', color: 'var(--sub-color)', lineHeight: '1.5' }} {...props} />
              ),
              // Style lists
              ul: ({ ...props }) => (
                <ul style={{ marginLeft: '20px', marginBottom: '8px', color: 'var(--sub-color)' }} {...props} />
              ),
              ol: ({ ...props }) => (
                <ol style={{ marginLeft: '20px', marginBottom: '8px', color: 'var(--sub-color)' }} {...props} />
              ),
              li: ({ ...props }) => (
                <li style={{ marginBottom: '4px', lineHeight: '1.4' }} {...props} />
              ),
              // Style links
              a: ({ ...props }) => (
                <a style={{ color: 'var(--accent-color)', textDecoration: 'underline' }} {...props} />
              ),
              // Style strong/bold
              strong: ({ ...props }) => (
                <strong style={{ color: 'var(--main-color)', fontWeight: '700' }} {...props} />
              ),
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      )}

      {!isExpanded && (
        <div style={{ marginTop: '15px', textAlign: 'center', color: 'var(--sub-color)', fontSize: '12px' }}>
          Click to expand
        </div>
      )}
    </div>
  )
}

'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

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
    <div className="inline-block mb-6">
      <div
        className="bg-white border-2 border-[#323232] rounded-md p-5 flex flex-direction-column justify-start gap-2.5 font-sans transition-all hover:shadow-[6px_6px_0px_0px_#323232]"
        style={{
          boxShadow: '4px 4px 0px 0px #323232',
          width: '280px',
          minHeight: isExpanded ? '400px' : '320px',
        }}
      >
        {/* Icon/Image Area */}
        <div className="flex justify-center transition-all hover:-translate-y-1">
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white text-3xl font-bold border-2 border-[#323232]">
            #{number}
          </div>
        </div>

        {/* Title */}
        <h3 className="text-xl font-medium text-center text-[#323232] leading-tight">
          {title}
        </h3>

        {/* Subtitle */}
        <p className="text-sm text-[#666] line-clamp-2 min-h-[40px]">
          {subtitle}
        </p>

        {/* Innovation Type Badge */}
        <div className="flex justify-center">
          <span className="px-3 py-1 bg-gray-100 text-xs font-medium text-[#323232] rounded-full border border-[#323232] capitalize">
            {innovationType}
          </span>
        </div>

        {/* Divider */}
        <div className="w-full border-t border-[#323232] rounded-full" />

        {/* Expanded Content */}
        {isExpanded && (
          <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700 text-sm overflow-y-auto max-h-64">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                // Prevent dangerous elements (XSS protection)
                script: () => null,
                iframe: () => null,
                object: () => null,
                embed: () => null,
                // Style headings
                h1: ({ ...props }) => <h1 className="text-lg font-bold mt-3 mb-2" {...props} />,
                h2: ({ ...props }) => <h2 className="text-base font-semibold mt-3 mb-2" {...props} />,
                h3: ({ ...props }) => <h3 className="text-sm font-semibold mt-2 mb-1" {...props} />,
                // Style lists
                ul: ({ ...props }) => <ul className="list-disc list-inside space-y-1 my-2 text-xs" {...props} />,
                ol: ({ ...props }) => <ol className="list-decimal list-inside space-y-1 my-2 text-xs" {...props} />,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}

        {/* Footer Button */}
        <div className="mt-auto flex justify-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-9 bg-white border-2 border-[#323232] rounded-md px-4 transition-all hover:border-[#2d8cf0] active:translate-y-1"
          >
            <svg
              className="w-5 h-5 fill-[#323232] transition-all hover:fill-[#2d8cf0]"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              {isExpanded ? (
                <path d="M19 13H5v-2h14v2z" />
              ) : (
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
              )}
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

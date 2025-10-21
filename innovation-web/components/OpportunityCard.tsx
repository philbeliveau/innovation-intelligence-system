'use client'

import { useState } from 'react'
import OpportunityModal from './OpportunityModal'
import { cn } from '@/lib/utils'
import { Sparkles } from 'lucide-react'

interface OpportunityCardProps {
  number: number
  title: string
  markdown: string
}

export default function OpportunityCard({ number, title, markdown }: OpportunityCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)

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

  // Color scheme based on opportunity number (similar to TrackCard)
  const getColorClasses = (num: number) => {
    const colors = [
      'from-teal-400 to-teal-600',
      'from-blue-400 to-blue-600',
      'from-purple-400 to-purple-600',
      'from-orange-400 to-orange-600',
      'from-pink-400 to-pink-600',
    ]
    return colors[(num - 1) % colors.length]
  }

  return (
    <>
      <div
        className={cn(
          'flex cursor-pointer items-start gap-4 rounded-xl bg-white p-4 shadow-sm transition-all',
          'border-2 border-gray-200 hover:shadow-md hover:border-teal-300'
        )}
        onClick={() => setIsModalOpen(true)}
      >
        {/* Opportunity Icon with Colored Background */}
        <div className="flex-shrink-0">
          <div
            className={cn(
              'flex h-16 w-16 items-center justify-center rounded-lg bg-gradient-to-br',
              getColorClasses(number)
            )}
          >
            <div className="text-center">
              <Sparkles className="h-6 w-6 text-white mb-1 mx-auto" />
              <div className="text-white text-xs font-bold">#{number}</div>
            </div>
          </div>
        </div>

        {/* Opportunity Content */}
        <div className="flex-1 space-y-2">
          {/* Title - Bold and prominent */}
          <h3 className="text-base font-bold text-gray-900 line-clamp-2">{title}</h3>

          {/* Summary - Clear and readable */}
          <p className="text-sm leading-snug text-gray-600 line-clamp-2">{subtitle}</p>

          {/* Innovation Type Badge */}
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700 capitalize">
              {innovationType}
            </span>
            <span className="text-xs text-gray-400">Click to view details</span>
          </div>
        </div>
      </div>

      {/* Modal */}
      <OpportunityModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        number={number}
        title={title}
        markdown={markdown}
        innovationType={innovationType}
      />
    </>
  )
}

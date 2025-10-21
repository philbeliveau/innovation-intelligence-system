'use client'

import { useState } from 'react'
import OpportunityModal from './OpportunityModal'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

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

  // Color scheme for gradient hero based on opportunity number
  const getGradientClasses = (num: number) => {
    const gradients = [
      'from-teal-200 to-teal-400',
      'from-blue-200 to-blue-400',
      'from-purple-200 to-purple-400',
      'from-orange-200 to-orange-400',
      'from-pink-200 to-pink-400',
    ]
    return gradients[(num - 1) % gradients.length]
  }

  return (
    <>
      <div
        className={cn(
          'group relative w-full max-w-full sm:max-w-[280px] bg-white p-3 sm:p-4 transition-all cursor-pointer',
          'border-[3px] sm:border-[5px] border-black shadow-[6px_6px_0_#000] sm:shadow-[8px_8px_0_#000]',
          'hover:translate-x-[-2px] hover:translate-y-[-2px] sm:hover:translate-x-[-3px] sm:hover:translate-y-[-3px] hover:shadow-[8px_8px_0_#000] sm:hover:shadow-[11px_11px_0_#000]'
        )}
        onClick={() => setIsModalOpen(true)}
      >
        {/* Hero Image Gradient with Opportunity Number - Reduced height on mobile */}
        <div className={cn(
          'mb-3 h-24 sm:h-32 w-full bg-gradient-to-br flex items-center justify-center',
          getGradientClasses(number)
        )}>
          <div className="text-center">
            <div className="text-3xl sm:text-5xl font-black text-black/20">#{number}</div>
          </div>
        </div>

        {/* Title with Underline Animation - Responsive text size */}
        <h2 className="relative mb-2 sm:mb-3 overflow-hidden text-lg sm:text-xl font-black uppercase leading-tight text-black">
          {title}
          <span className="absolute bottom-0 left-0 h-[2px] w-[90%] translate-x-[-100%] bg-black transition-transform duration-300 group-hover:translate-x-0" />
        </h2>

        {/* Innovation Type Badge */}
        <div className="mb-3 flex flex-wrap gap-1.5">
          <Badge className="border border-black bg-orange-500 px-2 py-0.5 text-xs font-semibold text-white uppercase">
            {innovationType}
          </Badge>
        </div>

        {/* Summary */}
        <p className="mb-3 text-sm leading-snug text-black line-clamp-3">{subtitle}</p>

        {/* Pagination Dots */}
        <div className="flex justify-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-black" />
          <div className="h-1.5 w-1.5 rounded-full bg-black" />
          <div className="h-1.5 w-1.5 rounded-full bg-black" />
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

'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Star } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'

interface OpportunityCard {
  id: string
  number: number
  title: string
  content: string
  isStarred: boolean
}

interface RunDetailOpportunityCardsProps {
  cards: OpportunityCard[]
  onStarToggle: (cardId: string) => void
}

export default function RunDetailOpportunityCards({
  cards,
  onStarToggle,
}: RunDetailOpportunityCardsProps) {
  const [expandedCard, setExpandedCard] = useState<OpportunityCard | null>(null)

  return (
    <>
      {/* Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cards.map((card) => (
          <Card
            key={card.id}
            className="border-[5px] border-[#5B9A99] shadow-[8px_8px_0px_0px_rgba(91,154,153,1)] transition-all duration-200 hover:-translate-x-[3px] hover:-translate-y-[3px] hover:shadow-[11px_11px_0px_0px_rgba(91,154,153,1)] cursor-pointer relative"
            onClick={() => setExpandedCard(card)}
          >
            {/* Star Button */}
            <Button
              variant="ghost"
              size="icon"
              className="absolute top-4 right-4 z-10 hover:bg-yellow-100"
              onClick={(e) => {
                e.stopPropagation()
                onStarToggle(card.id)
              }}
            >
              <Star
                className={`w-5 h-5 ${
                  card.isStarred
                    ? 'fill-yellow-500 text-yellow-500'
                    : 'text-gray-400'
                }`}
              />
            </Button>

            <CardContent className="p-6 pr-14">
              {/* Card Number */}
              <div className="text-xs font-mono text-[#5B9A99] mb-2">CARD {card.number}</div>

              {/* Title */}
              <h3 className="text-xl font-black mb-4 line-clamp-2 text-[#5B9A99]">{card.title}</h3>

              {/* Content Preview */}
              <div className="text-sm text-gray-700 line-clamp-4 prose prose-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypeSanitize]}
                >
                  {card.content}
                </ReactMarkdown>
              </div>

              {/* Read More Hint */}
              <div className="mt-4 text-xs text-gray-500 font-mono">
                CLICK TO EXPAND →
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {cards.length === 0 && (
        <div className="text-center py-20 border-4 border-[#5B9A99]">
          <h2 className="text-2xl font-bold mb-2 text-[#5B9A99]">No opportunity cards</h2>
          <p className="text-gray-600">This run did not generate any opportunity cards.</p>
        </div>
      )}

      {/* Expanded Card Modal */}
      <Dialog open={!!expandedCard} onOpenChange={() => setExpandedCard(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto border-4 border-[#5B9A99]">
          <DialogHeader className="sticky top-0 bg-white z-10 pb-4 border-b-4 border-[#5B9A99] mb-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="text-xs font-mono text-[#5B9A99] mb-2">
                  CARD {expandedCard?.number}
                </div>
                <DialogTitle className="text-2xl font-black text-[#5B9A99]">
                  {expandedCard?.title}
                </DialogTitle>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 hover:bg-yellow-100"
                onClick={() => expandedCard && onStarToggle(expandedCard.id)}
              >
                <Star
                  className={`w-6 h-6 ${
                    expandedCard?.isStarred
                      ? 'fill-yellow-500 text-yellow-500'
                      : 'text-gray-400'
                  }`}
                />
              </Button>
            </div>
          </DialogHeader>

          {/* Full Content - Notion-style formatting */}
          <div className="p-6 sm:p-8">
            <div className="max-w-3xl mx-auto">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeSanitize]}
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
                {expandedCard?.content || ''}
              </ReactMarkdown>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

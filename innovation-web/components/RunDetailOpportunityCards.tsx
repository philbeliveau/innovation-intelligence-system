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
            className="border-[5px] border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all duration-200 hover:-translate-x-[3px] hover:-translate-y-[3px] hover:shadow-[11px_11px_0px_0px_rgba(0,0,0,1)] cursor-pointer relative"
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
              <div className="text-xs font-mono text-gray-500 mb-2">CARD {card.number}</div>

              {/* Title */}
              <h3 className="text-xl font-black mb-4 line-clamp-2">{card.title}</h3>

              {/* Content Preview */}
              <div className="text-sm text-gray-700 line-clamp-4 prose prose-sm">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{card.content}</ReactMarkdown>
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
        <div className="text-center py-20 border-4 border-black">
          <h2 className="text-2xl font-bold mb-2">No opportunity cards</h2>
          <p className="text-gray-600">This run did not generate any opportunity cards.</p>
        </div>
      )}

      {/* Expanded Card Modal */}
      <Dialog open={!!expandedCard} onOpenChange={() => setExpandedCard(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto border-4 border-black">
          <DialogHeader className="sticky top-0 bg-white z-10 pb-4 border-b-4 border-black mb-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="text-xs font-mono text-gray-500 mb-2">
                  CARD {expandedCard?.number}
                </div>
                <DialogTitle className="text-2xl font-black">
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

          {/* Full Content */}
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {expandedCard?.content || ''}
            </ReactMarkdown>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

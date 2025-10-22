'use client'

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'

interface LatentFactor {
  mechanismTitle: string
  mechanismType: string
  constraintEliminated: string
}

interface DocumentCardProps {
  title: string
  summary: string
  industry: string
  theme: string
  sources: string[]
  latentFactors?: LatentFactor[]
  onClick?: () => void
  onDownload?: () => void
  blobUrl?: string
  fileName?: string
}

export default function DocumentCard({
  title,
  summary,
  industry,
  theme,
  sources,
  latentFactors,
  onClick,
}: DocumentCardProps) {
  const [isMechanismsModalOpen, setIsMechanismsModalOpen] = useState(false)
  // Format sources to show first source + count of others
  const displaySource = sources.length > 0 ? sources[0] : ''
  const otherSourcesCount = sources.length > 1 ? sources.length - 1 : 0

  return (
    <div
      className={cn(
        'group relative w-full max-w-full sm:max-w-[480px] bg-white p-4 sm:p-6 transition-all',
        'border-[3px] sm:border-[5px] border-black shadow-[6px_6px_0_#000] sm:shadow-[8px_8px_0_#000]',
        onClick && 'cursor-pointer hover:translate-x-[-2px] hover:translate-y-[-2px] sm:hover:translate-x-[-3px] sm:hover:translate-y-[-3px] hover:shadow-[8px_8px_0_#000] sm:hover:shadow-[11px_11px_0_#000]'
      )}
      onClick={onClick}
    >
      {/* Hero Image Placeholder - Reduced height on mobile */}
      <div className="mb-3 h-24 sm:h-32 w-full bg-gradient-to-br from-amber-200 to-amber-400" />

      {/* Title with Underline Animation - Responsive text size */}
      <h2 className="relative mb-2 sm:mb-3 overflow-hidden text-lg sm:text-xl font-black uppercase leading-tight text-black">
        {title}
        <span className="absolute bottom-0 left-0 h-[2px] w-[90%] translate-x-[-100%] bg-black transition-transform duration-300 group-hover:translate-x-0" />
      </h2>

      {/* Badges */}
      <div className="mb-3 flex flex-wrap gap-1.5">
        {/* Source */}
        <Badge variant="secondary" className="border border-black bg-gray-700 px-2 py-0.5 text-xs font-semibold text-white">
          {displaySource}
        </Badge>
        {otherSourcesCount > 0 && (
          <Badge variant="secondary" className="border border-black bg-gray-700 px-2 py-0.5 text-xs font-semibold text-white">
            +{otherSourcesCount}
          </Badge>
        )}

        {/* Industry */}
        <Badge className="border border-black bg-orange-500 px-2 py-0.5 text-xs font-semibold text-white">
          {industry}
        </Badge>

        {/* Theme */}
        <Badge className="border border-black bg-red-600 px-2 py-0.5 text-xs font-semibold text-white">
          {theme}
        </Badge>
      </div>

      {/* Summary */}
      <p className="mb-3 text-sm leading-snug text-black">{summary}</p>

      {/* Innovation Mechanisms - Latent Factors */}
      {latentFactors && latentFactors.length > 0 && (
        <div
          className={cn(
            'mb-3 border-2 border-black bg-amber-50 p-3 transition-all',
            'cursor-pointer hover:border-[3px] hover:bg-amber-100'
          )}
          onClick={(e) => {
            e.stopPropagation()
            setIsMechanismsModalOpen(true)
          }}
        >
          <div className="mb-2 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-base">💡</span>
              <h3 className="text-xs font-bold uppercase">Innovation Mechanisms</h3>
            </div>
            <span className="text-[10px] font-bold text-gray-600">Click to explore →</span>
          </div>
          {latentFactors.map((factor, idx) => (
            <div key={idx} className="mb-2 last:mb-0">
              <div className="mb-1 inline-block bg-black px-2 py-0.5 text-[10px] font-bold uppercase text-white">
                {factor.mechanismType}
              </div>
              <p className="mb-0.5 text-xs font-bold leading-tight">{factor.mechanismTitle}</p>
              <p className="text-[11px] text-gray-600">→ {factor.constraintEliminated}</p>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Dots */}
      <div className="flex justify-center gap-1.5">
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
      </div>

      {/* Innovation Mechanisms Modal */}
      <Dialog open={isMechanismsModalOpen} onOpenChange={setIsMechanismsModalOpen}>
        <DialogContent className="max-w-2xl border-4 border-black bg-white shadow-[12px_12px_0_#000]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-2xl font-black uppercase">
              <span className="text-2xl">💡</span>
              Innovation Mechanisms
            </DialogTitle>
            <DialogDescription className="text-sm text-gray-600">
              These are the underlying patterns that make innovations work — the HOW and WHY, not just the WHAT.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 mt-4">
            {latentFactors && latentFactors.map((factor, idx) => (
              <div
                key={idx}
                className="border-2 border-black bg-amber-50 p-4 hover:bg-amber-100 transition-colors"
              >
                {/* Mechanism Type Badge */}
                <div className="mb-3 inline-block bg-black px-3 py-1.5 text-xs font-bold uppercase text-white">
                  {factor.mechanismType}
                </div>

                {/* Mechanism Title */}
                <h3 className="mb-2 text-base font-bold leading-tight text-black">
                  {factor.mechanismTitle}
                </h3>

                {/* Constraint Eliminated */}
                <div className="flex items-start gap-2">
                  <span className="text-sm font-bold text-gray-700">Constraint Eliminated:</span>
                  <p className="text-sm text-gray-700 flex-1">
                    {factor.constraintEliminated}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

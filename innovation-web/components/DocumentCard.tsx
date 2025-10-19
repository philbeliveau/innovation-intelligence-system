import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface DocumentCardProps {
  title: string
  summary: string
  industry: string
  theme: string
  sources: string[]
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
  onClick,
}: DocumentCardProps) {
  // Format sources to show first source + count of others
  const displaySource = sources.length > 0 ? sources[0] : ''
  const otherSourcesCount = sources.length > 1 ? sources.length - 1 : 0

  return (
    <div
      className={cn(
        'group relative w-full max-w-[280px] bg-white p-4 transition-all',
        'border-[5px] border-black shadow-[8px_8px_0_#000]',
        onClick && 'cursor-pointer hover:translate-x-[-3px] hover:translate-y-[-3px] hover:shadow-[11px_11px_0_#000]'
      )}
      onClick={onClick}
    >
      {/* Hero Image Placeholder */}
      <div className="mb-3 h-32 w-full bg-gradient-to-br from-amber-200 to-amber-400" />

      {/* Title with Underline Animation */}
      <h2 className="relative mb-3 overflow-hidden text-xl font-black uppercase leading-tight text-black">
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

      {/* Pagination Dots */}
      <div className="flex justify-center gap-1.5">
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
        <div className="h-1.5 w-1.5 rounded-full bg-black" />
      </div>
    </div>
  )
}

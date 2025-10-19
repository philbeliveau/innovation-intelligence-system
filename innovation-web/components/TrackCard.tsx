import { cn } from '@/lib/utils'

interface TrackCardProps {
  trackNumber: number
  title: string
  summary: string
  selected: boolean
  onSelect: () => void
}

export default function TrackCard({
  trackNumber,
  title,
  summary,
  selected,
  onSelect,
}: TrackCardProps) {
  return (
    <div
      className={cn(
        'flex cursor-pointer items-center gap-4 rounded-xl bg-white p-4 shadow-sm transition-all',
        selected
          ? 'border-3 border-teal-500 shadow-md ring-2 ring-teal-200'
          : 'border-2 border-gray-200 opacity-60 hover:opacity-85 hover:shadow-md'
      )}
      onClick={onSelect}
    >
      {/* Track Icon with Colored Background */}
      <div className="flex-shrink-0">
        <div
          className={cn(
            'flex h-16 w-16 items-center justify-center rounded-lg',
            trackNumber === 1 && 'bg-gradient-to-br from-teal-400 to-teal-600',
            trackNumber === 2 && 'bg-gradient-to-br from-orange-400 to-orange-600'
          )}
        >
          <svg
            className="h-8 w-8 text-white"
            viewBox="0 0 100 100"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <rect x="10" y="20" width="20" height="60" fill="currentColor" rx="2" />
            <rect x="40" y="10" width="20" height="80" fill="currentColor" rx="2" />
            <rect x="70" y="30" width="20" height="50" fill="currentColor" rx="2" />
            <circle cx="20" cy="15" r="8" fill="#FFD700" />
          </svg>
        </div>
      </div>

      {/* Track Content */}
      <div className="flex-1 space-y-1.5">
        {/* Title - Bold and prominent */}
        <h3 className="text-base font-bold text-gray-900">{title}</h3>

        {/* Summary - Clear and readable */}
        <p className="text-sm leading-snug text-gray-600 line-clamp-2">{summary}</p>
      </div>
    </div>
  )
}

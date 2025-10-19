import { Card, CardContent, CardHeader } from '@/components/ui/card'
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
    <Card
      className={cn(
        'cursor-pointer transition-all',
        selected
          ? 'border-2 border-blue-500 bg-blue-50'
          : 'border-gray-300 opacity-60 hover:opacity-80'
      )}
      onClick={onSelect}
    >
      <CardHeader>
        <div className="flex items-center gap-2">
          {/* Radio Button */}
          <input
            type="radio"
            checked={selected}
            onChange={onSelect}
            className="h-4 w-4 cursor-pointer"
            aria-label={`Select Track ${trackNumber}`}
          />
          <span className="font-medium text-gray-900">Track {trackNumber}</span>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {/* Icon Placeholder */}
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gray-200">
          <span className="text-xl">💡</span>
        </div>

        {/* Title */}
        <h3 className="font-medium text-gray-900">{title}</h3>

        {/* Summary */}
        <p className="text-sm text-gray-600">{summary}</p>
      </CardContent>
    </Card>
  )
}

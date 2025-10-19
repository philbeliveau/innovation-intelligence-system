import { Card, CardContent, CardHeader } from '@/components/ui/card'

interface IdeationTracksSidebarProps {
  trackNumber: number
  title: string
  summary: string
}

export default function IdeationTracksSidebar({ trackNumber, title, summary }: IdeationTracksSidebarProps) {
  // Truncate summary to first 100 characters
  const truncatedSummary = summary.length > 100
    ? summary.substring(0, 100) + '...'
    : summary

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 opacity-60" data-testid={`sidebar-track-${trackNumber}`}>
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 font-semibold text-sm">
            {trackNumber}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-700 mb-1 truncate" data-testid="sidebar-track-title">
              {title}
            </h4>
            <p className="text-xs text-gray-500" data-testid="sidebar-track-summary">
              {truncatedSummary}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

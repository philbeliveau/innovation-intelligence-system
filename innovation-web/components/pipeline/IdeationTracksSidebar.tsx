// Sidebar component for displaying non-selected ideation track

interface IdeationTracksSidebarProps {
  trackNumber: number
  title: string
  summary: string
}

export default function IdeationTracksSidebar({ trackNumber, title, summary }: IdeationTracksSidebarProps) {
  return (
    <div
      className="h-[140px] flex-shrink-0 bg-white rounded-lg shadow-sm border border-gray-200 border-l-4 border-l-teal-200 hover:border-l-[#5B9A99] transition-colors duration-200"
      data-testid={`sidebar-track-${trackNumber}`}
    >
      <div className="p-4 flex flex-col h-full">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-8 h-8 bg-[#5B9A99] rounded-full flex items-center justify-center text-white font-semibold text-sm">
            {trackNumber}
          </div>
          <div className="flex-1 min-w-0 overflow-hidden">
            <h4 className="text-sm font-semibold text-gray-900 mb-1.5 truncate" data-testid="sidebar-track-title">
              {title}
            </h4>
            <p className="text-xs text-gray-500 line-clamp-3 leading-relaxed" data-testid="sidebar-track-summary">
              {summary}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * ModeIndicator - Shows whether pipeline is live or retrospective
 * Story 10.7: Dual-mode pipeline viewing support
 */

type ModeIndicatorProps = {
  mode: 'live' | 'retrospective'
  completedAt?: string | null
}

export function ModeIndicator({ mode, completedAt }: ModeIndicatorProps) {
  if (mode === 'live') {
    return null
  }

  return (
    <div className="flex items-center gap-2 mb-4">
      <div className="h-2 w-2 bg-blue-500 rounded-full" />
      <span className="text-sm text-gray-600">
        Completed Analysis
        {completedAt && ` (${new Date(completedAt).toLocaleDateString()})`}
      </span>
    </div>
  )
}

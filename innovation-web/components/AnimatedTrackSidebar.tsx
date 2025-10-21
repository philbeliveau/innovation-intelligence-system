import { cn } from '@/lib/utils'
import TrackCard from '@/components/TrackCard'

interface Track {
  title: string
  summary: string
  icon_url?: string
}

interface AnimatedTrackSidebarProps {
  track: Track | null
  show: boolean
}

export default function AnimatedTrackSidebar({
  track,
  show
}: AnimatedTrackSidebarProps) {
  if (!track) return null

  return (
    <div
      className={cn(
        'transition-all duration-500 ease-out',
        show ? 'opacity-100 scale-100' : 'opacity-0 scale-90 -translate-x-10'
      )}
    >
      <TrackCard
        trackNumber={0}
        title={track.title}
        summary={track.summary.slice(0, 100) + '...'}
        selected={false}
        onSelect={() => {}}
        compactMode
        disabled
      />
    </div>
  )
}

import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface PipelineTrackCardProps {
  trackNumber: number
  title: string
  summary: string
}

export default function PipelineTrackCard({ trackNumber, title, summary }: PipelineTrackCardProps) {
  return (
    <Card className="relative" data-testid={`track-card-${trackNumber}`}>
      <div className="absolute top-4 right-4">
        <Badge variant="default" className="bg-green-500 hover:bg-green-600" data-testid="selected-badge">
          ✓ Selected
        </Badge>
      </div>
      <CardHeader>
        <h3 className="text-lg font-semibold" data-testid="track-title">
          Track {trackNumber}: {title}
        </h3>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-700" data-testid="track-summary">{summary}</p>
      </CardContent>
    </Card>
  )
}

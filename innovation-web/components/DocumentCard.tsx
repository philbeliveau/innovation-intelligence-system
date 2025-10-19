import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Download } from 'lucide-react'

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
  onDownload,
  blobUrl,
  fileName,
}: DocumentCardProps) {
  // Format sources to show first source + count of others
  const displaySource = sources.length > 0 ? sources[0] : ''
  const otherSourcesCount = sources.length > 1 ? sources.length - 1 : 0

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card click
    if (onDownload) {
      onDownload()
    } else if (blobUrl && fileName) {
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  return (
    <Card
      className={`h-full ${onClick ? 'cursor-pointer transition-shadow hover:shadow-lg' : ''}`}
      onClick={onClick}
    >
      {/* Hero Image Placeholder */}
      <div className="h-48 w-full bg-gradient-to-br from-amber-200 to-amber-400" />

      <CardHeader className="relative">
        <h2 className="pr-10 text-xl font-semibold text-gray-900">{title}</h2>
        {/* Download Button (Story 2.2.1) */}
        {(onDownload || (blobUrl && fileName)) && (
          <div className="absolute right-4 top-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDownload}
              aria-label="Download document"
              className="h-8 w-8"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Badges */}
        <div className="flex flex-wrap gap-2">
          {/* Source Badges */}
          {displaySource && (
            <Badge variant="secondary" className="bg-gray-600 text-white hover:bg-gray-700">
              {displaySource}
            </Badge>
          )}
          {otherSourcesCount > 0 && (
            <Badge variant="secondary" className="bg-gray-600 text-white hover:bg-gray-700">
              {otherSourcesCount} {otherSourcesCount === 1 ? 'other' : 'others'}
            </Badge>
          )}

          {/* Industry Badge */}
          <Badge className="bg-orange-500 text-white hover:bg-orange-600">
            {industry}
          </Badge>

          {/* Theme Badge */}
          <Badge className="bg-red-600 text-white hover:bg-red-700">
            {theme}
          </Badge>
        </div>

        {/* Summary */}
        <p className="text-sm text-gray-700">{summary}</p>

        {/* Pagination Indicator (3 dots) */}
        <div className="flex justify-center gap-2 pt-4">
          <div className="h-2 w-2 rounded-full bg-gray-400" />
          <div className="h-2 w-2 rounded-full bg-gray-400" />
          <div className="h-2 w-2 rounded-full bg-gray-400" />
        </div>
      </CardContent>
    </Card>
  )
}

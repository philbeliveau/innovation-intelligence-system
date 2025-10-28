import Image from 'next/image'
import { SparksIcon } from '../icons'

interface SparkPreview {
  number: number
  title: string
  summary: string
  heroImageUrl?: string
}

interface SparksPreviewColumnProps {
  sparks: SparkPreview[]
  isGenerating: boolean
}

const SparkPreviewCard: React.FC<SparkPreview> = ({ number, title, summary, heroImageUrl }) => (
  <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-4">
    <div className="relative aspect-video">
      {heroImageUrl ? (
        <Image src={heroImageUrl} alt={title} fill className="object-cover" />
      ) : (
        <div className="w-full h-full bg-gray-200 flex items-center justify-center">
          <span className="text-gray-400 text-xs">No image</span>
        </div>
      )}
      <div className="absolute top-2 left-2 w-8 h-8 bg-white rounded-full flex items-center justify-center font-bold text-sm shadow-md">
        {number}
      </div>
    </div>
    <div className="p-3">
      <h4 className="font-semibold text-sm line-clamp-1">{title}</h4>
      <p className="text-xs text-gray-600 line-clamp-2 mt-1">{summary}</p>
    </div>
  </div>
)

export const SparksPreviewColumn: React.FC<SparksPreviewColumnProps> = ({
  sparks,
  isGenerating,
}) => {
  // Only show first 2 sparks
  const previewSparks = sparks.slice(0, 2)

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <SparksIcon />
        <h3 className="text-lg font-semibold text-gray-900">Sparks</h3>
      </div>

      {/* Preview Cards */}
      <div>
        {previewSparks.map((spark) => (
          <SparkPreviewCard key={spark.number} {...spark} />
        ))}
      </div>

      {/* Generating Text */}
      {isGenerating && (
        <p className="text-sm text-gray-500 italic mt-2">
          More sparks generating...
        </p>
      )}
    </div>
  )
}

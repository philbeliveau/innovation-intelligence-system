import Image from 'next/image'
import { SparksIcon } from '../icons'
import { getCardColorGradient } from '@/lib/card-colors'

interface SparkPreview {
  number: number
  title: string
  summary: string
  heroImageUrl?: string
  isPlaceholder?: boolean
}

interface SparksPreviewColumnProps {
  sparks: SparkPreview[]
  isGenerating: boolean
  onCardClick?: (index: number) => void
}

interface SparkPreviewCardProps extends SparkPreview {
  onClick?: () => void
}

const SparkPreviewCard: React.FC<SparkPreviewCardProps> = ({ number, title, summary, heroImageUrl, isPlaceholder, onClick }) => {
  const gradientClass = getCardColorGradient(number)

  return (
    <div
      className={`bg-white rounded-lg shadow-sm overflow-hidden mb-4 transition-all duration-200 ${
        isPlaceholder ? 'opacity-60' : 'cursor-pointer hover:shadow-md hover:scale-[1.02]'
      }`}
      onClick={!isPlaceholder ? onClick : undefined}
    >
      <div className="relative aspect-video">
        {heroImageUrl ? (
          <Image src={heroImageUrl} alt={title} fill className="object-cover" />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${gradientClass} flex items-center justify-center ${isPlaceholder ? 'animate-pulse' : ''}`}>
            <span className="text-white/30 text-4xl font-bold">{isPlaceholder ? '✨' : number}</span>
          </div>
        )}
        <div className={`absolute top-2 left-2 w-8 h-8 bg-white rounded-full flex items-center justify-center font-bold text-sm shadow-md ${isPlaceholder ? 'opacity-50' : ''}`}>
          {number}
        </div>
      </div>
      <div className="p-3">
        <h4 className={`font-semibold text-sm line-clamp-1 ${isPlaceholder ? 'text-gray-400 italic' : ''}`}>{title}</h4>
        <p className={`text-xs text-gray-600 line-clamp-2 mt-1 ${isPlaceholder ? 'text-gray-400 italic' : ''}`}>{summary}</p>
      </div>
    </div>
  )
}

export const SparksPreviewColumn: React.FC<SparksPreviewColumnProps> = ({
  sparks,
  isGenerating,
  onCardClick,
}) => {
  // Only show first 2 sparks
  const previewSparks = sparks.slice(0, 2)

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 flex-1">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <SparksIcon />
        <h3 className="text-lg font-semibold text-gray-900">Sparks</h3>
      </div>

      {/* Preview Cards */}
      <div>
        {previewSparks.map((spark, index) => (
          <SparkPreviewCard
            key={spark.number}
            {...spark}
            onClick={() => onCardClick?.(index)}
          />
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

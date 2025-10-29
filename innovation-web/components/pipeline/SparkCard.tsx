import Image from 'next/image'
import { getCardColorGradient } from '@/lib/card-colors'

interface Spark {
  id: string
  title: string
  summary: string
  heroImageUrl?: string
  content: string // Markdown content
}

interface SparkCardProps {
  spark: Spark
  number: number
  onClick: () => void
}

export default function SparkCard({ spark, number, onClick }: SparkCardProps) {
  const gradientClass = getCardColorGradient(number)

  return (
    <div
      onClick={onClick}
      className="
        bg-white rounded-lg shadow-md overflow-hidden cursor-pointer
        transition-all duration-300 ease-in-out
        hover:shadow-xl hover:scale-[1.02]
        active:scale-[0.98]
        min-h-[200px]
      "
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      }}
      aria-label={`View spark ${number}: ${spark.title}`}
    >
      {/* Hero Image with Number Overlay */}
      <div className={`relative aspect-video ${!spark.heroImageUrl ? `bg-gradient-to-br ${gradientClass}` : ''}`}>
        {spark.heroImageUrl ? (
          <Image
            src={spark.heroImageUrl}
            alt={spark.title}
            fill
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-white/20 text-8xl font-bold">{number}</span>
          </div>
        )}
        <div className="absolute bottom-3 right-3 w-12 h-12 bg-white rounded-full flex items-center justify-center shadow-lg">
          <span className="text-xl font-bold text-gray-900">{number}</span>
        </div>
      </div>

      {/* Card Content */}
      <div className="p-4 md:p-6">
        <h3 className="text-lg md:text-xl font-semibold mb-2 line-clamp-2">{spark.title}</h3>
        <p className="text-sm text-gray-600 mb-4 line-clamp-3 md:line-clamp-4">{spark.summary}</p>
        <button
          className="
            ml-auto px-4 py-2
            bg-[#5B9A99] text-white rounded-md
            hover:bg-[#4A7F7E] active:bg-[#3A6F6E]
            transition-colors
            flex items-center gap-2
            min-h-[44px]
          "
          onClick={(e) => {
            e.stopPropagation()
            onClick()
          }}
          aria-label={`View details for ${spark.title}`}
        >
          View →
        </button>
      </div>
    </div>
  )
}

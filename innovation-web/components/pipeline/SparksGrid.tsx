import SparkCard from './SparkCard'
import { SlideUpTransition } from '../animations/SlideUpTransition'

interface Spark {
  id: string
  title: string
  summary: string
  heroImageUrl?: string
  content: string
}

interface SparksGridProps {
  sparks: Spark[]
  onCardClick: (sparkId: string) => void
}

export default function SparksGrid({ sparks, onCardClick }: SparksGridProps) {
  if (!sparks || sparks.length === 0) {
    return (
      <div className="max-w-screen-xl mx-auto px-4 md:px-6 py-6 md:py-8 mb-20 md:mb-24 text-center">
        <p className="text-gray-500">No sparks generated yet.</p>
      </div>
    )
  }

  return (
    <div className="max-w-screen-xl mx-auto px-4 md:px-6 py-6 md:py-8 mb-20 md:mb-24 safe-bottom">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        {sparks.map((spark, index) => (
          <SlideUpTransition key={spark.id} isVisible={true} index={index}>
            <SparkCard
              spark={spark}
              number={index + 1}
              onClick={() => onCardClick(spark.id)}
            />
          </SlideUpTransition>
        ))}
      </div>
    </div>
  )
}

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
      <div className="max-w-screen-xl mx-auto px-6 py-8 mb-24 text-center">
        <p className="text-gray-500">No sparks generated yet.</p>
      </div>
    )
  }

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-8 mb-24">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
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

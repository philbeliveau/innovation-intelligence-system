import Image from 'next/image'
import { SignalIcon } from '../icons'

interface SignalsColumnProps {
  trendImage?: string
  trendTitle: string
  trendDescription?: string
}

export const SignalsColumn: React.FC<SignalsColumnProps> = ({
  trendImage,
  trendTitle,
  trendDescription,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <SignalIcon />
        <h3 className="text-lg font-semibold text-gray-900">Signals</h3>
      </div>

      {/* Trend Image */}
      <div className="mb-4 rounded-lg overflow-hidden">
        {trendImage ? (
          <div className="relative w-full aspect-video">
            <Image
              src={trendImage}
              alt={trendTitle}
              fill
              className="object-cover"
            />
          </div>
        ) : (
          <div className="w-full aspect-video bg-gray-200 flex items-center justify-center">
            <span className="text-gray-400 text-sm">No image available</span>
          </div>
        )}
      </div>

      {/* Trend Title */}
      <h4 className="font-semibold text-base text-gray-900 line-clamp-2 mb-2">
        {trendTitle}
      </h4>

      {/* Trend Description (optional) */}
      {trendDescription && (
        <p className="text-sm text-gray-600 line-clamp-3">{trendDescription}</p>
      )}
    </div>
  )
}

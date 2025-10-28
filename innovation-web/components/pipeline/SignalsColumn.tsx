import Image from 'next/image'
import { SignalIcon } from '../icons'
import { Plus } from 'lucide-react'

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
    <div className="flex flex-col h-full max-w-sm">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <SignalIcon />
        <h3 className="text-lg font-semibold text-gray-900">Signals</h3>
      </div>

      {/* Signal Card - Matches mockup page 3 design */}
      <div className="relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex-1 min-h-[400px] flex flex-col">
        {/* Hero Image with overlay title */}
        <div className="relative w-full flex-1">
          {trendImage ? (
            <div className="relative w-full h-full">
              <Image
                src={trendImage}
                alt={trendTitle}
                fill
                className="object-cover"
              />
            </div>
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-teal-100 to-teal-50" />
          )}

          {/* Title overlay at bottom */}
          <div className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-sm p-4">
            <p className="text-sm text-gray-900 font-medium leading-relaxed">
              {trendTitle}
            </p>
          </div>
        </div>

        {/* Plus button */}
        <div className="p-4 border-t border-gray-100 bg-white">
          <button className="w-full flex items-center justify-center gap-2 text-teal-600 hover:text-teal-700 text-sm font-medium">
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

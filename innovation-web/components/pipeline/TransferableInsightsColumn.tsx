import { useState } from 'react'
import { InsightsIcon } from '../icons'
import { X } from 'lucide-react'

interface TransferableInsightsColumnProps {
  coreMechanism: string
  businessImpact: string
  patternTransfersTo: string[]
  runId: string
  onDownload: () => void
  onClick?: () => void
}

/**
 * Parse core mechanism text to extract top 3 mechanisms
 * Handles various formats: numbered lists, bullet points, or paragraphs
 */
const parseCoreMechanisms = (text: string): string[] => {
  // Try to split by numbered patterns first (1., 2., 3. or 1), 2), 3))
  const numberedPattern = /(?:\d+[.)]\s*)/g
  const parts = text.split(numberedPattern).filter(Boolean)

  if (parts.length >= 2) {
    return parts.slice(0, 3).map(p => p.trim())
  }

  // Try bullet points or dashes
  const bulletPattern = /(?:[•\-*]\s*)/g
  const bulletParts = text.split(bulletPattern).filter(Boolean)

  if (bulletParts.length >= 2) {
    return bulletParts.slice(0, 3).map(p => p.trim())
  }

  // Fallback: split by periods and take first 3 sentences
  const sentences = text.split(/\.\s+/).filter(Boolean)
  return sentences.slice(0, 3).map(s => s.trim() + (s.endsWith('.') ? '' : '.'))
}

export const TransferableInsightsColumn: React.FC<TransferableInsightsColumnProps> = ({
  coreMechanism,
  businessImpact,
  patternTransfersTo,
  onDownload,
  onClick,
}) => {
  const [showPreview, setShowPreview] = useState(false)
  const top3Mechanisms = parseCoreMechanisms(coreMechanism)

  const handleClick = () => {
    setShowPreview(true)
    onClick?.()
  }

  return (
    <>
      <div
        className={`bg-white rounded-lg shadow-sm p-6 flex flex-col flex-1 ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
        onClick={onClick ? handleClick : undefined}
      >
        {/* Header */}
        <div className="flex items-center gap-2 mb-4">
          <InsightsIcon />
          <h3 className="text-lg font-semibold text-gray-900">Transferable Insights</h3>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto max-h-[500px] space-y-4">
          {/* Core Mechanism Section */}
          <div>
            <h4 className="font-semibold text-sm text-gray-700 mb-2">Core Mechanism</h4>
            <p className="text-sm text-gray-600 line-clamp-3">{coreMechanism}</p>
            {onClick && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleClick()
                }}
                className="text-xs font-medium text-[#5B9A99] hover:text-[#4a7f7e] mt-2"
              >
                View top 3 mechanisms →
              </button>
            )}
          </div>

          {/* Business Impact Section */}
          <div>
            <h4 className="font-semibold text-sm text-gray-700 mb-2">Business Impact</h4>
            <p className="text-sm text-gray-600">{businessImpact}</p>
          </div>

          {/* Pattern Transfers To Section */}
          <div>
            <h4 className="font-semibold text-sm text-gray-700 mb-2">Pattern Transfers To</h4>
            <ul className="list-disc list-inside space-y-1">
              {patternTransfersTo.map((industry, index) => (
                <li key={index} className="text-sm text-gray-600">
                  {industry}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Download Link */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDownload()
            }}
            className="text-sm font-medium text-[#5B9A99] hover:text-[#4a7f7e] underline"
          >
            View/download extraction report
          </button>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowPreview(false)}
        >
          <div
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <InsightsIcon />
                <h3 className="text-xl font-semibold text-gray-900">Top 3 Core Mechanisms</h3>
              </div>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Close preview"
              >
                <X size={24} />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-140px)]">
              {top3Mechanisms.length > 0 ? (
                <ol className="space-y-4">
                  {top3Mechanisms.map((mechanism, index) => (
                    <li key={index} className="flex gap-4">
                      <span className="flex-shrink-0 w-8 h-8 bg-[#5B9A99] text-white rounded-full flex items-center justify-center font-semibold">
                        {index + 1}
                      </span>
                      <p className="flex-1 text-gray-700 leading-relaxed pt-1">
                        {mechanism}
                      </p>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className="text-gray-600 italic">No mechanisms extracted yet</p>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 bg-[#5B9A99] text-white rounded-lg hover:bg-[#4a7f7e] transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

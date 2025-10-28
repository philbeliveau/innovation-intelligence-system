import { InsightsIcon } from '../icons'

interface TransferableInsightsColumnProps {
  coreMechanism: string
  businessImpact: string
  patternTransfersTo: string[]
  runId: string
  onDownload: () => void
}

export const TransferableInsightsColumn: React.FC<TransferableInsightsColumnProps> = ({
  coreMechanism,
  businessImpact,
  patternTransfersTo,
  onDownload,
}) => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 flex flex-col">
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
          <p className="text-sm text-gray-600">{coreMechanism}</p>
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
          onClick={onDownload}
          className="text-sm font-medium text-[#5B9A99] hover:text-[#4a7f7e] underline"
        >
          View/download extraction report
        </button>
      </div>
    </div>
  )
}

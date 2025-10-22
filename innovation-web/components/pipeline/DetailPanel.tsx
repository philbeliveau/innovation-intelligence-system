import { Card, CardContent } from '@/components/ui/card'
import { useRouter } from 'next/navigation'

interface DetailPanelProps {
  currentStage: number
  status: 'running' | 'complete' | 'error'
  runId: string
  brandName?: string
}

const stageDescriptions = [
  { name: 'Track Division', description: 'Selected 2 inspiration tracks' },
  { name: 'Signal Amplification', description: 'Extracting broader trends' },
  { name: 'Universal Translation', description: 'Converting to brand-agnostic lessons' },
  { name: 'Brand Contextualization', description: 'Applying to your brand' },
  { name: 'Opportunity Generation', description: 'Creating 5 actionable innovations' }
]

export default function DetailPanel({ currentStage, status, runId, brandName }: DetailPanelProps) {
  const router = useRouter()

  if (status === 'complete') {
    return (
      <div
        className="mt-4 sm:mt-6 bg-gradient-to-r from-amber-200 to-amber-400 border-[3px] sm:border-[5px] border-black shadow-[4px_4px_0_#000] sm:shadow-[8px_8px_0_#000]"
        data-testid="detail-panel-complete"
      >
        <div className="flex flex-col items-center justify-center p-6 sm:p-8">
          <div className="text-center mb-4 sm:mb-6">
            <h3 className="text-2xl sm:text-3xl font-black uppercase text-black mb-2 sm:mb-3">
              Pipeline Complete! 🎉
            </h3>
            <p className="text-base sm:text-lg font-bold text-black">
              Your innovation opportunities are ready to view.
            </p>
          </div>
          <button
            onClick={() => router.push(`/results/${runId}`)}
            className="bg-orange-500 text-white px-6 sm:px-8 py-3 sm:py-4 font-black uppercase text-base sm:text-lg border-[3px] sm:border-4 border-black shadow-[4px_4px_0_#000] sm:shadow-[6px_6px_0_#000] hover:shadow-[6px_6px_0_#000] sm:hover:shadow-[8px_8px_0_#000] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all active:shadow-[2px_2px_0_#000] active:translate-x-[2px] active:translate-y-[2px] w-full sm:w-auto"
            data-testid="view-opportunities-button"
          >
            View Opportunities →
          </button>
        </div>
      </div>
    )
  }

  if (currentStage < 1 || currentStage > 5) {
    return null
  }

  const stage = stageDescriptions[currentStage - 1]
  const stageWithBrand = currentStage === 4 && brandName
    ? { ...stage, description: `Applying to ${brandName}` }
    : stage

  return (
    <Card className="mt-6" data-testid="detail-panel-running">
      <CardContent className="p-6">
        <div className="flex items-center gap-4">
          <div className="flex-shrink-0">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900" data-testid="stage-name">
              Stage {currentStage}: {stageWithBrand.name}
            </h3>
            <p className="text-sm text-gray-600 mt-1" data-testid="stage-description">{stageWithBrand.description}...</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

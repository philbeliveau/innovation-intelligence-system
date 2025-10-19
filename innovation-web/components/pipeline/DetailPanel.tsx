import { Button } from '@/components/ui/button'
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
      <Card className="mt-6" data-testid="detail-panel-complete">
        <CardContent className="flex flex-col items-center justify-center p-8">
          <div className="text-center mb-4">
            <h3 className="text-2xl font-bold text-green-600 mb-2">Pipeline Complete! 🎉</h3>
            <p className="text-gray-600">Your innovation opportunities are ready to view.</p>
          </div>
          <Button
            onClick={() => router.push(`/results/${runId}`)}
            size="lg"
            className="bg-blue-600 hover:bg-blue-700"
            data-testid="view-opportunities-button"
          >
            View Opportunities →
          </Button>
        </CardContent>
      </Card>
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

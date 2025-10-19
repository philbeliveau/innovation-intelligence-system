import { cn } from '@/lib/utils'

interface StageBoxProps {
  stageNumber: number
  stageName: string
  status: 'completed' | 'running' | 'pending'
}

export default function StageBox({ stageNumber, stageName, status }: StageBoxProps) {
  const statusIcon = {
    completed: '✓',
    running: '⏳',
    pending: '⌛'
  }[status]

  const statusClass = {
    completed: 'bg-green-500 text-white',
    running: 'bg-blue-500 text-white animate-pulse border-2 border-blue-700',
    pending: 'bg-gray-300 text-gray-500 opacity-50'
  }[status]

  return (
    <div
      className={cn('flex flex-col items-center justify-center p-6 rounded-lg transition-all', statusClass)}
      data-testid={`stage-box-${stageNumber}`}
      data-stage={stageNumber}
      data-status={status}
    >
      <span className="text-sm font-semibold">Stage {stageNumber}</span>
      <span className="text-xs mt-1">{stageName}</span>
      <span className="text-3xl mt-2">{statusIcon}</span>
    </div>
  )
}

import { cn } from '@/lib/utils'
import { Check, Loader2, Circle } from 'lucide-react'

interface StageBoxProps {
  stageNumber: number
  stageName: string
  status: 'completed' | 'running' | 'pending'
}

export default function StageBox({ stageNumber, stageName, status }: StageBoxProps) {
  // Elegant icon components instead of emoji
  const StatusIcon = {
    completed: Check,
    running: Loader2,
    pending: Circle
  }[status]

  const iconClassName = {
    completed: 'h-5 w-5 sm:h-6 sm:w-6',
    running: 'h-5 w-5 sm:h-6 sm:w-6 animate-spin',
    pending: 'h-5 w-5 sm:h-6 sm:w-6'
  }[status]

  // Brand-aligned teal color palette
  const statusClass = {
    completed: 'bg-[#5B9A99] text-white border border-[#5B9A99]',
    running: 'bg-teal-50/30 backdrop-blur-sm border-2 border-[#6BAAA9] shadow-lg shadow-teal-100 text-[#5B9A99]',
    pending: 'bg-gray-50 text-gray-400 border border-gray-200'
  }[status]

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 rounded-xl transition-all duration-300',
        statusClass
      )}
      data-testid={`stage-box-${stageNumber}`}
      data-stage={stageNumber}
      data-status={status}
      role="status"
      aria-label={`Stage ${stageNumber}: ${stageName} - ${status}`}
    >
      <span className="text-[10px] sm:text-xs font-medium opacity-70">Stage {stageNumber}</span>
      <span className="text-xs sm:text-sm font-semibold mt-1 sm:mt-1.5">{stageName}</span>
      <div className="mt-2 sm:mt-3">
        <StatusIcon className={iconClassName} aria-hidden="true" />
      </div>
    </div>
  )
}

import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface StageBoxProps {
  stageNumber: number
  stageName: string
  status: 'completed' | 'running' | 'pending'
}

export default function StageBox({ stageNumber, stageName, status }: StageBoxProps) {
  // Minimal dot icons - sleek and modern
  const StatusIcon = ({className}: {className: string}) => {
    if (status === 'completed') {
      return (
        <div className={cn('rounded-full bg-white', className)} aria-hidden="true" />
      )
    }
    if (status === 'running') {
      return <Loader2 className={cn(className, 'animate-spin')} aria-hidden="true" />
    }
    return (
      <div className={cn('rounded-full border-2 border-current', className)} aria-hidden="true" />
    )
  }

  const iconClassName = 'h-3 w-3 sm:h-4 sm:w-4'

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
        <StatusIcon className={iconClassName} />
      </div>
    </div>
  )
}

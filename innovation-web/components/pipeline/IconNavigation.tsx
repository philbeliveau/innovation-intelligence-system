import { SignalIcon, InsightsIcon, SparksIcon } from '@/components/icons'

interface IconNavigationProps {
  activeSection: 'signals' | 'insights' | 'sparks'
  onNavigate?: (section: 'signals' | 'insights' | 'sparks') => void
}

export default function IconNavigation({ activeSection, onNavigate }: IconNavigationProps) {
  const sections = [
    { id: 'signals' as const, label: 'Signals', Icon: SignalIcon },
    { id: 'insights' as const, label: 'Insights', Icon: InsightsIcon },
    { id: 'sparks' as const, label: 'Sparks', Icon: SparksIcon },
  ]

  return (
    <div className="flex justify-center gap-6 md:gap-12 py-4 md:py-6 mb-4 md:mb-6 border-b border-gray-200">
      {sections.map(({ id, label, Icon }) => (
        <button
          key={id}
          onClick={() => onNavigate?.(id)}
          className={`
            flex flex-col items-center gap-1 md:gap-2
            transition-colors
            min-w-[44px] min-h-[44px]
            ${activeSection === id ? 'text-[#5B9A99]' : 'text-gray-400'}
          `}
          aria-label={`Navigate to ${label}`}
        >
          <Icon className="w-6 h-6 md:w-8 md:h-8" />
          {/* Labels: Show on tablet+, hide on mobile to save space */}
          <span className="hidden md:inline text-xs font-medium">{label}</span>
        </button>
      ))}
    </div>
  )
}

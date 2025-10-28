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
    <div className="flex justify-center gap-12 py-6 mb-6 border-b border-gray-200">
      {sections.map(({ id, label, Icon }) => (
        <button
          key={id}
          onClick={() => onNavigate?.(id)}
          className={`flex flex-col items-center gap-2 transition-colors ${
            activeSection === id ? 'text-[#5B9A99]' : 'text-gray-400'
          }`}
          aria-label={`Navigate to ${label}`}
        >
          <Icon className="w-8 h-8" />
          <span className="text-xs font-medium">{label}</span>
        </button>
      ))}
    </div>
  )
}

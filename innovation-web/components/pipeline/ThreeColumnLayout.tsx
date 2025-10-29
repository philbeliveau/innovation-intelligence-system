import { cn } from '@/lib/utils'

interface ThreeColumnLayoutProps {
  children: React.ReactNode
  className?: string
}

export const ThreeColumnLayout: React.FC<ThreeColumnLayoutProps> = ({
  children,
  className
}) => {
  return (
    <div className={cn(
      // Mobile: Single column stack
      "flex flex-col",
      // Tablet: 2 columns (Signals + Insights top, Sparks bottom full-width)
      "md:grid md:grid-cols-2 md:auto-rows-min",
      // Desktop: 3 columns side-by-side
      "lg:flex lg:flex-row",
      // Spacing: Compact on mobile, spacious on desktop
      "gap-4 md:gap-4 lg:gap-6",
      "bg-gray-50 p-4 md:p-6",
      "transition-all duration-800 ease-in-out",
      "items-start",
      className
    )}>
      {children}
    </div>
  )
}

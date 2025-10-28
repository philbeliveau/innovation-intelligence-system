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
      "grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3",
      "gap-4 md:gap-4 lg:gap-6",
      "bg-gray-50 p-6",
      "transition-all duration-800 ease-in-out",
      className
    )}>
      {children}
    </div>
  )
}

import { ReactNode } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { useWillChange } from '@/hooks/useWillChange'
import { DURATION, EASING_FUNCTION, calculateStaggerDelay } from '@/lib/transitions'

interface SlideUpTransitionProps {
  /** Controls visibility and triggers transition */
  isVisible: boolean
  /** Duration in milliseconds (default: 800) */
  duration?: number
  /** Delay between staggered items in ms (default: 100) */
  staggerDelay?: number
  /** Index for stagger calculation (default: 0) */
  index?: number
  /** Maximum items to stagger (default: 6) */
  maxStagger?: number
  /** Content to animate */
  children: ReactNode
  /** Additional CSS classes */
  className?: string
}

/**
 * SlideUpTransition - Slide up + fade transition with stagger support
 *
 * Used for State 2 → State 3 transitions. Cards slide up 20px while fading in.
 * Supports staggered animation for multiple cards (capped at maxStagger).
 *
 * Performance:
 * - Uses transform + opacity (GPU-accelerated)
 * - Applies will-change temporarily during animation
 *
 * @example
 * {cards.map((card, index) => (
 *   <SlideUpTransition key={card.id} isVisible={true} index={index}>
 *     <CardContent />
 *   </SlideUpTransition>
 * ))}
 */
export const SlideUpTransition = ({
  isVisible,
  duration = DURATION.SLIDE_UP,
  staggerDelay = DURATION.STAGGER_DELAY,
  index = 0,
  maxStagger = 6,
  children,
  className = ''
}: SlideUpTransitionProps) => {
  const reducedMotion = useReducedMotion()
  const ref = useWillChange(isVisible)

  // Calculate actual timing
  const actualDuration = reducedMotion ? 0 : duration
  const delay = reducedMotion ? 0 : calculateStaggerDelay(index, maxStagger)

  return (
    <div
      ref={ref as React.RefObject<HTMLDivElement>}
      className={`transition-all ${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? 'translateY(0)' : 'translateY(20px)',
        transitionDuration: `${actualDuration}ms`,
        transitionDelay: `${delay}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        transitionProperty: 'opacity, transform'
      }}
      aria-hidden={!isVisible}
    >
      {children}
    </div>
  )
}

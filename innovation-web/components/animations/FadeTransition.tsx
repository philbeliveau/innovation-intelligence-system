import { ReactNode } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { DURATION, EASING_FUNCTION } from '@/lib/transitions'

interface FadeTransitionProps {
  /** Controls visibility and triggers transition */
  isVisible: boolean
  /** Duration in milliseconds (default: 600) */
  duration?: number
  /** Content to animate */
  children: ReactNode
  /** Callback fired when transition completes */
  onTransitionEnd?: () => void
  /** Additional CSS classes */
  className?: string
}

/**
 * FadeTransition - Smooth opacity transition wrapper
 *
 * Used for State 1 ↔ State 2 transitions. Respects user's reduced motion
 * preference by setting duration to 0ms when enabled.
 *
 * Performance: Uses only opacity (GPU-accelerated property)
 *
 * @example
 * <FadeTransition isVisible={stage === 2}>
 *   <StateContent />
 * </FadeTransition>
 */
export const FadeTransition = ({
  isVisible,
  duration = DURATION.FADE,
  children,
  onTransitionEnd,
  className = ''
}: FadeTransitionProps) => {
  const reducedMotion = useReducedMotion()
  const actualDuration = reducedMotion ? 0 : duration

  return (
    <div
      className={`transition-opacity ${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transitionDuration: `${actualDuration}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        // Only show in DOM when visible or transitioning
        display: isVisible || actualDuration > 0 ? 'block' : 'none'
      }}
      onTransitionEnd={onTransitionEnd}
      aria-hidden={!isVisible}
    >
      {children}
    </div>
  )
}

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
 * FadeTransition - Smooth opacity transition wrapper with absolute positioning
 *
 * Used for State 1 ↔ State 2 transitions. Respects user's reduced motion
 * preference by setting duration to 0ms when enabled.
 *
 * IMPORTANT: Uses absolute positioning to create overlay effect.
 * Parent container MUST have `position: relative` and defined height.
 *
 * Performance: Uses only opacity (GPU-accelerated property)
 *
 * @example
 * <div className="relative min-h-screen">
 *   <FadeTransition isVisible={stage === 1}>
 *     <State1Content />
 *   </FadeTransition>
 *   <FadeTransition isVisible={stage === 2}>
 *     <State2Content />
 *   </FadeTransition>
 * </div>
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
      className={`absolute inset-0 transition-opacity ${className}`}
      style={{
        opacity: isVisible ? 1 : 0,
        transitionDuration: `${actualDuration}ms`,
        transitionTimingFunction: EASING_FUNCTION,
        // Prevent interaction when not visible
        pointerEvents: isVisible ? 'auto' : 'none',
        // Keep in DOM for transition but hide when invisible AND transition done
        visibility: isVisible || actualDuration > 0 ? 'visible' : 'hidden'
      }}
      onTransitionEnd={onTransitionEnd}
      aria-hidden={!isVisible}
    >
      {children}
    </div>
  )
}

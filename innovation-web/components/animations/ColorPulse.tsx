import { useEffect, useState } from 'react'
import { DURATION } from '@/lib/transitions'

interface ColorPulseProps {
  /** Teal color from BOI branding (default: #5B9A99) */
  color?: string
  /** Duration of pulse in ms (default: 150) */
  duration?: number
  /** Callback fired when pulse completes */
  onComplete?: () => void
}

/**
 * ColorPulse - Accessibility fallback for reduced motion preference
 *
 * Provides visual feedback when animations are disabled. Shows a brief
 * teal background flash (150ms) instead of animated transitions.
 *
 * Used automatically by animation components when prefers-reduced-motion
 * is detected.
 *
 * @example
 * {reducedMotion && <ColorPulse onComplete={handleTransition} />}
 */
export const ColorPulse = ({
  color = 'rgba(91, 154, 153, 0.1)', // Teal with 10% opacity
  duration = DURATION.COLOR_PULSE,
  onComplete
}: ColorPulseProps) => {
  const [isPulsing, setIsPulsing] = useState(false)

  useEffect(() => {
    // Start pulse
    setIsPulsing(true)

    // End pulse after duration
    const timeout = setTimeout(() => {
      setIsPulsing(false)
      onComplete?.()
    }, duration)

    return () => clearTimeout(timeout)
  }, [duration, onComplete])

  return (
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        backgroundColor: isPulsing ? color : 'transparent',
        transition: `background-color ${duration}ms ease-in-out`,
        zIndex: 50
      }}
      aria-hidden="true"
    />
  )
}

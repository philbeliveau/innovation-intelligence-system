import { useEffect, useState } from 'react'

/**
 * Hook to detect user's reduced motion preference
 *
 * Respects the prefers-reduced-motion media query for accessibility.
 * When enabled, all animations should be disabled or replaced with
 * instant transitions and alternative feedback mechanisms.
 *
 * @returns {boolean} true if user prefers reduced motion
 *
 * @example
 * const reducedMotion = useReducedMotion()
 * const duration = reducedMotion ? 0 : 600
 */
export const useReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false)

  useEffect(() => {
    // Check initial preference
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)

    // Listen for changes (user can toggle system setting during session)
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches)
    }

    mediaQuery.addEventListener('change', handleChange)

    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }, [])

  return prefersReducedMotion
}

'use client'

import { useEffect, useState } from 'react'
import { BREAKPOINTS, Breakpoint, getCurrentBreakpoint } from '@/lib/breakpoints'

/**
 * Hook to detect current responsive breakpoint
 *
 * Returns the current breakpoint based on window width:
 * - mobile: < 768px
 * - tablet: 768px - 1023px
 * - desktop: 1024px - 1439px
 * - wide: >= 1440px
 *
 * @example
 * ```tsx
 * const breakpoint = useBreakpoint()
 *
 * if (breakpoint === 'mobile') {
 *   return <MobileLayout />
 * }
 * ```
 */
export const useBreakpoint = (): Breakpoint => {
  // Default to 'desktop' for SSR
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('desktop')

  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth
      setBreakpoint(getCurrentBreakpoint(width))
    }

    // Set initial breakpoint
    updateBreakpoint()

    // Update on resize
    window.addEventListener('resize', updateBreakpoint)
    return () => window.removeEventListener('resize', updateBreakpoint)
  }, [])

  return breakpoint
}

/**
 * Hook to check if current viewport is at or above a specific breakpoint
 *
 * @example
 * ```tsx
 * const isTabletOrLarger = useBreakpointCheck('tablet')
 * ```
 */
export const useBreakpointCheck = (breakpoint: Breakpoint): boolean => {
  const currentBreakpoint = useBreakpoint()
  const currentWidth = typeof window !== 'undefined' ? window.innerWidth : 1024

  return currentWidth >= BREAKPOINTS[breakpoint]
}

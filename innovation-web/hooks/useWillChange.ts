import { useEffect, useRef } from 'react'

/**
 * Hook to manage will-change CSS property for GPU-accelerated animations
 *
 * Applies will-change: transform, opacity during animations for optimal
 * performance, then removes it after completion to avoid excessive GPU usage.
 *
 * IMPORTANT: Use sparingly - will-change has memory/performance costs.
 * Only apply during actual animations.
 *
 * @param {boolean} isAnimating - Whether animation is currently active
 * @returns {React.RefObject<HTMLElement>} Ref to attach to animated element
 *
 * @example
 * const ref = useWillChange(isVisible)
 * return <div ref={ref as any}>Content</div>
 */
export const useWillChange = (isAnimating: boolean) => {
  const ref = useRef<HTMLElement>(null)

  useEffect(() => {
    const element = ref.current
    if (!element) return

    if (isAnimating) {
      // Apply will-change during animation for GPU acceleration
      element.style.willChange = 'transform, opacity'
    } else {
      // Remove will-change after animation completes
      // Small delay to ensure transition has finished
      const timeout = setTimeout(() => {
        element.style.willChange = 'auto'
      }, 50)

      return () => clearTimeout(timeout)
    }
  }, [isAnimating])

  return ref
}

/**
 * Helper function to directly apply GPU optimizations to an element
 * Use when you can't use the hook (e.g., refs not available)
 *
 * @param {HTMLElement} element - DOM element to optimize
 *
 * @example
 * const div = document.querySelector('.animated')
 * applyGPUOptimizations(div)
 */
export const applyGPUOptimizations = (element: HTMLElement | null): void => {
  if (!element) return
  element.style.willChange = 'transform, opacity'
}

/**
 * Remove GPU optimizations from an element
 *
 * @param {HTMLElement} element - DOM element to clean up
 *
 * @example
 * removeGPUOptimizations(div)
 */
export const removeGPUOptimizations = (element: HTMLElement | null): void => {
  if (!element) return
  element.style.willChange = 'auto'
}

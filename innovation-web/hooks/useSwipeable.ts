'use client'

import { useRef, TouchEvent } from 'react'

interface SwipeHandlers {
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  onSwipeUp?: () => void
  onSwipeDown?: () => void
  threshold?: number        // Minimum distance in pixels (default: 50)
  timeThreshold?: number    // Maximum duration in ms (default: 300)
}

interface TouchPosition {
  x: number
  y: number
  time: number
}

/**
 * Hook for handling touch swipe gestures
 *
 * @param handlers - Swipe event handlers and configuration
 * @returns Touch event handlers to spread on the target element
 *
 * @example
 * ```tsx
 * const swipeHandlers = useSwipeable({
 *   onSwipeLeft: () => console.log('Swiped left'),
 *   onSwipeRight: () => console.log('Swiped right'),
 *   threshold: 50,      // Minimum 50px swipe distance
 *   timeThreshold: 300  // Maximum 300ms swipe duration
 * })
 *
 * return <div {...swipeHandlers}>Swipeable content</div>
 * ```
 */
export const useSwipeable = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  threshold = 50,
  timeThreshold = 300,
}: SwipeHandlers) => {
  const touchStart = useRef<TouchPosition | null>(null)

  const handleTouchStart = (e: TouchEvent) => {
    touchStart.current = {
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
      time: Date.now(),
    }
  }

  const handleTouchEnd = (e: TouchEvent) => {
    if (!touchStart.current) return

    const deltaX = e.changedTouches[0].clientX - touchStart.current.x
    const deltaY = e.changedTouches[0].clientY - touchStart.current.y
    const deltaTime = Date.now() - touchStart.current.time

    // Ignore if gesture took too long
    if (deltaTime > timeThreshold) {
      touchStart.current = null
      return
    }

    const absDeltaX = Math.abs(deltaX)
    const absDeltaY = Math.abs(deltaY)

    // Determine if swipe is primarily horizontal or vertical
    const isHorizontal = absDeltaX > absDeltaY

    if (isHorizontal && absDeltaX > threshold) {
      // Horizontal swipe
      if (deltaX > 0 && onSwipeRight) {
        onSwipeRight()
      } else if (deltaX < 0 && onSwipeLeft) {
        onSwipeLeft()
      }
    } else if (!isHorizontal && absDeltaY > threshold) {
      // Vertical swipe
      if (deltaY > 0 && onSwipeDown) {
        onSwipeDown()
      } else if (deltaY < 0 && onSwipeUp) {
        onSwipeUp()
      }
    }

    touchStart.current = null
  }

  return {
    onTouchStart: handleTouchStart,
    onTouchEnd: handleTouchEnd,
  }
}

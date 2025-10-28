import { useEffect, useRef } from 'react'

interface StateAnnouncerProps {
  /** Message to announce to screen readers */
  message: string
  /** Politeness level (default: 'polite') */
  ariaLive?: 'polite' | 'assertive'
}

/**
 * StateAnnouncer - Announces state changes to screen readers
 *
 * Provides accessibility support for state transitions by announcing
 * changes via aria-live regions. Essential for users relying on
 * assistive technology.
 *
 * @example
 * <StateAnnouncer message="Pipeline complete. Displaying 12 sparks." />
 */
export const StateAnnouncer = ({
  message,
  ariaLive = 'polite'
}: StateAnnouncerProps) => {
  const announcerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Update aria-live region when message changes
    if (announcerRef.current && message) {
      announcerRef.current.textContent = message
    }
  }, [message])

  return (
    <div
      ref={announcerRef}
      role="status"
      aria-live={ariaLive}
      aria-atomic="true"
      className="sr-only"
    >
      {message}
    </div>
  )
}

/**
 * Helper hook to announce state changes
 * Returns a function to trigger announcements
 *
 * @example
 * const announce = useStateAnnouncer()
 * announce('Stage 2 complete')
 */
export const useStateAnnouncer = () => {
  const announcerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Create announcer element if not exists
    if (!announcerRef.current) {
      const div = document.createElement('div')
      div.setAttribute('role', 'status')
      div.setAttribute('aria-live', 'polite')
      div.setAttribute('aria-atomic', 'true')
      div.className = 'sr-only'
      document.body.appendChild(div)
      announcerRef.current = div
    }

    return () => {
      if (announcerRef.current) {
        document.body.removeChild(announcerRef.current)
        announcerRef.current = null
      }
    }
  }, [])

  return (message: string) => {
    if (announcerRef.current) {
      announcerRef.current.textContent = message
    }
  }
}

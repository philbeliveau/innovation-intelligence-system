import { render, screen } from '@testing-library/react'
import { renderHook } from '@testing-library/react'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { FadeTransition } from '@/components/animations/FadeTransition'
import { SlideUpTransition } from '@/components/animations/SlideUpTransition'

describe('useReducedMotion hook', () => {
  const mockMatchMedia = (matches: boolean) => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)' ? matches : false,
        media: query,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        addListener: jest.fn(),
        removeListener: jest.fn(),
        dispatchEvent: jest.fn()
      }))
    })
  }

  it('returns false when prefers-reduced-motion is not set', () => {
    mockMatchMedia(false)
    const { result } = renderHook(() => useReducedMotion())
    expect(result.current).toBe(false)
  })

  it('returns true when prefers-reduced-motion is set', () => {
    mockMatchMedia(true)
    const { result } = renderHook(() => useReducedMotion())
    expect(result.current).toBe(true)
  })
})

describe('FadeTransition with reduced motion', () => {
  const mockMatchMedia = (matches: boolean) => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)' ? matches : false,
        media: query,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        addListener: jest.fn(),
        removeListener: jest.fn(),
        dispatchEvent: jest.fn()
      }))
    })
  }

  it('sets duration to 0ms when reduced motion is enabled', () => {
    mockMatchMedia(true)
    const { container } = render(
      <FadeTransition isVisible={true}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDuration).toBe('0ms')
  })

  it('uses normal duration when reduced motion is disabled', () => {
    mockMatchMedia(false)
    const { container } = render(
      <FadeTransition isVisible={true}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDuration).not.toBe('0ms')
  })
})

describe('SlideUpTransition with reduced motion', () => {
  const mockMatchMedia = (matches: boolean) => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: jest.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)' ? matches : false,
        media: query,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        addListener: jest.fn(),
        removeListener: jest.fn(),
        dispatchEvent: jest.fn()
      }))
    })
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('sets duration to 0ms when reduced motion is enabled', () => {
    mockMatchMedia(true)

    // Mock useWillChange to avoid ref issues in tests
    jest.mock('@/hooks/useWillChange', () => ({
      useWillChange: jest.fn(() => ({ current: null }))
    }))

    const { container } = render(
      <SlideUpTransition isVisible={true}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDuration).toBe('0ms')
  })

  it('sets stagger delay to 0ms when reduced motion is enabled', () => {
    mockMatchMedia(true)

    const { container } = render(
      <SlideUpTransition isVisible={true} index={5}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDelay).toBe('0ms')
  })
})

describe('Accessibility announcements', () => {
  it('renders StateAnnouncer with correct aria attributes', () => {
    const { StateAnnouncer } = require('@/components/animations/StateAnnouncer')
    const { container } = render(
      <StateAnnouncer message="Pipeline complete" />
    )

    const announcer = container.querySelector('[role="status"]')
    expect(announcer).toBeInTheDocument()
    expect(announcer).toHaveAttribute('aria-live', 'polite')
    expect(announcer).toHaveAttribute('aria-atomic', 'true')
  })

  it('StateAnnouncer is visually hidden but accessible', () => {
    const { StateAnnouncer } = require('@/components/animations/StateAnnouncer')
    const { container } = render(
      <StateAnnouncer message="Pipeline complete" />
    )

    const announcer = container.querySelector('[role="status"]')
    expect(announcer).toHaveClass('sr-only')
  })
})

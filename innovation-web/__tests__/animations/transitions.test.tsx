import { render, screen, waitFor } from '@testing-library/react'
import { FadeTransition } from '@/components/animations/FadeTransition'
import { SlideUpTransition } from '@/components/animations/SlideUpTransition'
import { DURATION } from '@/lib/transitions'

// Mock useReducedMotion hook
jest.mock('@/hooks/useReducedMotion', () => ({
  useReducedMotion: jest.fn(() => false)
}))

jest.mock('@/hooks/useWillChange', () => ({
  useWillChange: jest.fn(() => ({ current: null }))
}))

describe('FadeTransition', () => {
  it('renders children when visible', () => {
    render(
      <FadeTransition isVisible={true}>
        <div>Test Content</div>
      </FadeTransition>
    )
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies correct opacity when visible', () => {
    const { container } = render(
      <FadeTransition isVisible={true}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.opacity).toBe('1')
  })

  it('applies correct opacity when not visible', () => {
    const { container } = render(
      <FadeTransition isVisible={false}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.opacity).toBe('0')
  })

  it('uses correct transition duration', () => {
    const { container } = render(
      <FadeTransition isVisible={true}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDuration).toBe(`${DURATION.FADE}ms`)
  })

  it('hides content when not visible and no duration', () => {
    const { container } = render(
      <FadeTransition isVisible={false} duration={0}>
        <div>Test Content</div>
      </FadeTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.display).toBe('none')
  })
})

describe('SlideUpTransition', () => {
  it('renders children when visible', () => {
    render(
      <SlideUpTransition isVisible={true}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  it('applies correct transform when visible', () => {
    const { container } = render(
      <SlideUpTransition isVisible={true}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transform).toBe('translateY(0)')
  })

  it('applies correct transform when not visible', () => {
    const { container } = render(
      <SlideUpTransition isVisible={false}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transform).toBe('translateY(20px)')
  })

  it('applies stagger delay based on index', () => {
    const { container } = render(
      <SlideUpTransition isVisible={true} index={2}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDelay).toBe('200ms') // 2 * 100ms
  })

  it('caps stagger delay at maxStagger', () => {
    const { container } = render(
      <SlideUpTransition isVisible={true} index={10} maxStagger={6}>
        <div>Test Content</div>
      </SlideUpTransition>
    )
    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.style.transitionDelay).toBe('600ms') // capped at 6 * 100ms
  })
})

describe('Transition Timing', () => {
  it('FadeTransition completes within expected duration', async () => {
    jest.useFakeTimers()
    const onTransitionEnd = jest.fn()

    const { rerender } = render(
      <FadeTransition isVisible={false} onTransitionEnd={onTransitionEnd}>
        <div>Test Content</div>
      </FadeTransition>
    )

    rerender(
      <FadeTransition isVisible={true} onTransitionEnd={onTransitionEnd}>
        <div>Test Content</div>
      </FadeTransition>
    )

    // Fast-forward time
    jest.advanceTimersByTime(DURATION.FADE)

    // Trigger transition end manually (jsdom doesn't fire transitionend)
    const wrapper = screen.getByText('Test Content').parentElement
    const event = new Event('transitionend', { bubbles: true })
    wrapper?.dispatchEvent(event)

    expect(onTransitionEnd).toHaveBeenCalled()

    jest.useRealTimers()
  })
})

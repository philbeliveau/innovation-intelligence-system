/**
 * ExtractionAnimation Component Tests
 * Tests animation behavior, error states, and accessibility
 */

import { render, screen } from '@testing-library/react'
import ExtractionAnimation from '@/components/pipeline/ExtractionAnimation'

describe('ExtractionAnimation', () => {
  describe('Running State', () => {
    it('should render beaker SVG when status is running', () => {
      const { container } = render(<ExtractionAnimation status="running" />)

      // Check for beaker SVG elements
      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })

    it('should display correct text for running state', () => {
      render(<ExtractionAnimation status="running" />)

      expect(
        screen.getByText(/Extracting transferable insights from your document/i)
      ).toBeInTheDocument()
    })

    it('should show processing indicator when running', () => {
      render(<ExtractionAnimation status="running" />)

      expect(screen.getByText(/Processing.../i)).toBeInTheDocument()
    })

    it('should render BOI badge', () => {
      render(<ExtractionAnimation status="running" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveTextContent('BOI')
    })

    it('should show elapsed time when provided', () => {
      render(<ExtractionAnimation status="running" elapsedTime={5000} />)

      expect(screen.getByText(/Elapsed time: 5s/i)).toBeInTheDocument()
    })

    it('should render bubbles with animation class when running', () => {
      const { container } = render(<ExtractionAnimation status="running" />)

      const bubbles = container.querySelectorAll('.bubble-animation')
      expect(bubbles.length).toBeGreaterThan(0)
    })
  })

  describe('Error State', () => {
    it('should show error icon when status is error', () => {
      render(<ExtractionAnimation status="error" />)

      const errorIcon = screen.getByLabelText('Error')
      expect(errorIcon).toBeInTheDocument()
      expect(errorIcon).toHaveTextContent('⚠️')
    })

    it('should display error text when status is error', () => {
      render(<ExtractionAnimation status="error" />)

      expect(screen.getByText(/Extraction encountered an error/i)).toBeInTheDocument()
    })

    it('should render red overlay when status is error', () => {
      const { container } = render(<ExtractionAnimation status="error" />)

      const overlay = container.querySelector('.bg-red-500')
      expect(overlay).toBeInTheDocument()
      expect(overlay).toHaveClass('opacity-20')
    })

    it('should not show processing indicator in error state', () => {
      render(<ExtractionAnimation status="error" />)

      expect(screen.queryByText(/Processing.../i)).not.toBeInTheDocument()
    })

    it('should not render animated bubbles in error state', () => {
      const { container } = render(<ExtractionAnimation status="error" />)

      const bubbles = container.querySelectorAll('.bubble-animation')
      expect(bubbles.length).toBe(0)
    })
  })

  describe('Accessibility', () => {
    it('should have BOI badge with proper aria-label', () => {
      render(<ExtractionAnimation status="running" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toBeInTheDocument()
    })

    it('should have error icon with proper aria-label in error state', () => {
      render(<ExtractionAnimation status="error" />)

      const errorIcon = screen.getByLabelText('Error')
      expect(errorIcon).toBeInTheDocument()
    })

    it('should render SVG with aria-hidden in running state', () => {
      const { container } = render(<ExtractionAnimation status="running" />)

      const svg = container.querySelector('svg[aria-hidden="true"]')
      expect(svg).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('should render with proper container classes', () => {
      const { container } = render(<ExtractionAnimation status="running" />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('relative', 'h-full', 'flex', 'flex-col')
    })

    it('should center content vertically and horizontally', () => {
      const { container } = render(<ExtractionAnimation status="running" />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('items-center', 'justify-center')
    })
  })
})

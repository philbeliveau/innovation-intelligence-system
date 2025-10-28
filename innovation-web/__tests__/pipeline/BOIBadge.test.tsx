/**
 * BOIBadge Component Tests
 * Tests size variants, styling, and accessibility
 */

import { render, screen } from '@testing-library/react'
import BOIBadge from '@/components/pipeline/BOIBadge'

describe('BOIBadge', () => {
  describe('Rendering', () => {
    it('should render with default props', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toBeInTheDocument()
    })

    it('should display "BOI" text', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveTextContent('BOI')
    })

    it('should have teal background color', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('bg-[#5B9A99]')
    })

    it('should have white text color', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('text-white')
    })

    it('should be positioned absolutely', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('absolute')
    })

    it('should be positioned at top-left', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('top-4', 'left-4')
    })

    it('should be circular', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('rounded-full')
    })

    it('should be bold', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('font-bold')
    })
  })

  describe('Size Variants', () => {
    it('should render small size correctly', () => {
      render(<BOIBadge size="small" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('w-8', 'h-8', 'text-xs')
    })

    it('should render medium size correctly (default)', () => {
      render(<BOIBadge size="medium" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('w-12', 'h-12', 'text-sm')
    })

    it('should render large size correctly', () => {
      render(<BOIBadge size="large" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('w-16', 'h-16', 'text-base')
    })

    it('should default to medium size when size prop is omitted', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('w-12', 'h-12', 'text-sm')
    })
  })

  describe('Custom Styling', () => {
    it('should apply custom className', () => {
      render(<BOIBadge className="custom-class" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('custom-class')
    })

    it('should preserve default classes when custom className added', () => {
      render(<BOIBadge className="custom-class" />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('bg-[#5B9A99]', 'text-white', 'custom-class')
    })
  })

  describe('Accessibility', () => {
    it('should have proper aria-label', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveAttribute('aria-label', 'Board of Ideators')
    })

    it('should be findable by accessible name', () => {
      render(<BOIBadge />)

      expect(screen.getByLabelText('Board of Ideators')).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('should use flexbox for centering', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toHaveClass('flex', 'items-center', 'justify-center')
    })

    it('should be a div element', () => {
      render(<BOIBadge />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge.tagName).toBe('DIV')
    })
  })
})

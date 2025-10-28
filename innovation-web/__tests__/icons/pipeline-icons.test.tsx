import { render } from '@testing-library/react'
import { SignalIcon, InsightsIcon, SparksIcon } from '@/components/icons'

describe('Pipeline Icons', () => {
  describe('SignalIcon', () => {
    it('renders SVG with correct dimensions', () => {
      const { container } = render(<SignalIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toBeInTheDocument()
      expect(svg).toHaveAttribute('width', '24')
      expect(svg).toHaveAttribute('height', '24')
    })

    it('has aria-hidden attribute', () => {
      const { container } = render(<SignalIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveAttribute('aria-hidden', 'true')
    })

    it('applies custom className when provided', () => {
      const { container } = render(<SignalIcon className="custom-class" />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveClass('custom-class')
    })

    it('renders path with teal color', () => {
      const { container } = render(<SignalIcon />)
      const path = container.querySelector('path')

      expect(path).toHaveAttribute('stroke', '#5B9A99')
    })
  })

  describe('InsightsIcon', () => {
    it('renders SVG with correct dimensions', () => {
      const { container } = render(<InsightsIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toBeInTheDocument()
      expect(svg).toHaveAttribute('width', '24')
      expect(svg).toHaveAttribute('height', '24')
    })

    it('has aria-hidden attribute', () => {
      const { container } = render(<InsightsIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveAttribute('aria-hidden', 'true')
    })

    it('applies custom className when provided', () => {
      const { container } = render(<InsightsIcon className="custom-class" />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveClass('custom-class')
    })

    it('renders path with teal color', () => {
      const { container } = render(<InsightsIcon />)
      const path = container.querySelector('path')

      expect(path).toHaveAttribute('stroke', '#5B9A99')
    })
  })

  describe('SparksIcon', () => {
    it('renders SVG with correct dimensions', () => {
      const { container } = render(<SparksIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toBeInTheDocument()
      expect(svg).toHaveAttribute('width', '24')
      expect(svg).toHaveAttribute('height', '24')
    })

    it('has aria-hidden attribute', () => {
      const { container } = render(<SparksIcon />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveAttribute('aria-hidden', 'true')
    })

    it('applies custom className when provided', () => {
      const { container } = render(<SparksIcon className="custom-class" />)
      const svg = container.querySelector('svg')

      expect(svg).toHaveClass('custom-class')
    })

    it('renders path with teal color and fill', () => {
      const { container } = render(<SparksIcon />)
      const path = container.querySelector('path')

      expect(path).toHaveAttribute('stroke', '#5B9A99')
      expect(path).toHaveAttribute('fill', '#5B9A99')
      expect(path).toHaveAttribute('fillOpacity', '0.2')
    })
  })
})

/**
 * WorkflowIllustration Component Tests
 * Tests workflow visualization, image fallback, and animations
 */

import { render, screen, fireEvent } from '@testing-library/react'
import WorkflowIllustration from '@/components/pipeline/WorkflowIllustration'

describe('WorkflowIllustration', () => {
  describe('Default Rendering', () => {
    it('should render fallback SVG when no imageUrl provided', () => {
      const { container } = render(<WorkflowIllustration />)

      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })

    it('should render BOI badge', () => {
      render(<WorkflowIllustration />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toBeInTheDocument()
      expect(badge).toHaveTextContent('BOI')
    })

    it('should display correct heading text', () => {
      render(<WorkflowIllustration />)

      expect(screen.getByText(/Understanding the core transferable pattern/i)).toBeInTheDocument()
    })

    it('should display description text', () => {
      render(<WorkflowIllustration />)

      expect(
        screen.getByText(/Stage 1 analyzes your document to extract/i)
      ).toBeInTheDocument()
    })

    it('should render stage flow indicators', () => {
      render(<WorkflowIllustration />)

      expect(screen.getByText('Extract')).toBeInTheDocument()
      expect(screen.getByText('Amplify')).toBeInTheDocument()
      expect(screen.getByText('Translate')).toBeInTheDocument()
      expect(screen.getByText('Contextualize')).toBeInTheDocument()
      expect(screen.getByText('Generate')).toBeInTheDocument()
    })

    it('should highlight Extract stage as active', () => {
      const { container } = render(<WorkflowIllustration />)

      const extractStage = screen.getByText('Extract').closest('span')
      expect(extractStage).toHaveClass('bg-[#5B9A99]')
    })
  })

  describe('Custom Image', () => {
    it('should render image when imageUrl is provided', () => {
      render(<WorkflowIllustration imageUrl="https://example.com/workflow.png" />)

      const img = screen.getByAltText('Pipeline workflow illustration')
      expect(img).toBeInTheDocument()
      expect(img).toHaveAttribute('src', 'https://example.com/workflow.png')
    })

    it('should show fallback SVG when image fails to load', () => {
      const { container } = render(<WorkflowIllustration imageUrl="invalid-url.png" />)

      const img = screen.getByAltText('Pipeline workflow illustration')

      // Simulate image load error
      fireEvent.error(img)

      // After error, should show SVG
      const svg = container.querySelector('svg')
      expect(svg).toBeInTheDocument()
    })

    it('should use lazy loading for images', () => {
      render(<WorkflowIllustration imageUrl="https://example.com/workflow.png" />)

      const img = screen.getByAltText('Pipeline workflow illustration')
      expect(img).toHaveAttribute('loading', 'lazy')
    })
  })

  describe('Animations', () => {
    it('should apply breathing animation by default', () => {
      const { container } = render(<WorkflowIllustration />)

      const svg = container.querySelector('svg')
      expect(svg).toHaveClass('breathe-animation')
    })

    it('should not apply breathing animation when showAnimation is false', () => {
      const { container } = render(<WorkflowIllustration showAnimation={false} />)

      const svg = container.querySelector('svg')
      expect(svg).not.toHaveClass('breathe-animation')
    })

    it('should apply breathing animation to custom image', () => {
      render(<WorkflowIllustration imageUrl="https://example.com/workflow.png" />)

      const img = screen.getByAltText('Pipeline workflow illustration')
      expect(img).toHaveClass('breathe-animation')
    })

    it('should not apply animation to custom image when disabled', () => {
      render(
        <WorkflowIllustration imageUrl="https://example.com/workflow.png" showAnimation={false} />
      )

      const img = screen.getByAltText('Pipeline workflow illustration')
      expect(img).not.toHaveClass('breathe-animation')
    })
  })

  describe('Accessibility', () => {
    it('should have BOI badge with proper aria-label', () => {
      render(<WorkflowIllustration />)

      const badge = screen.getByLabelText('Board of Ideators')
      expect(badge).toBeInTheDocument()
    })

    it('should have SVG with aria-hidden', () => {
      const { container } = render(<WorkflowIllustration />)

      const svg = container.querySelector('svg[aria-hidden="true"]')
      expect(svg).toBeInTheDocument()
    })

    it('should have alt text for custom images', () => {
      render(<WorkflowIllustration imageUrl="https://example.com/workflow.png" />)

      const img = screen.getByAltText('Pipeline workflow illustration')
      expect(img).toBeInTheDocument()
    })
  })

  describe('Layout', () => {
    it('should render with proper container classes', () => {
      const { container } = render(<WorkflowIllustration />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('relative', 'h-full', 'flex', 'flex-col')
    })

    it('should center content', () => {
      const { container } = render(<WorkflowIllustration />)

      const wrapper = container.firstChild as HTMLElement
      expect(wrapper).toHaveClass('items-center', 'justify-center')
    })

    it('should have responsive max-width for image/svg', () => {
      const { container } = render(<WorkflowIllustration />)

      const contentWrapper = container.querySelector('.text-center')
      expect(contentWrapper).toHaveClass('w-full')
    })
  })
})

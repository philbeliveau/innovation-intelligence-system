import { render, screen } from '@testing-library/react'
import { SignalsColumn } from '@/components/pipeline/SignalsColumn'

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...props} />
  },
}))

describe('SignalsColumn', () => {
  it('renders header with icon and title', () => {
    render(<SignalsColumn trendTitle="Test Trend" />)

    expect(screen.getByText('Signals')).toBeInTheDocument()
  })

  it('displays trend title', () => {
    render(<SignalsColumn trendTitle="Amazing Food Trend" />)

    expect(screen.getByText('Amazing Food Trend')).toBeInTheDocument()
  })

  it('displays trend image when provided', () => {
    render(
      <SignalsColumn
        trendTitle="Test Trend"
        trendImage="https://example.com/image.jpg"
      />
    )

    const image = screen.getByAltText('Test Trend')
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', 'https://example.com/image.jpg')
  })

  it('shows placeholder when no image provided', () => {
    render(<SignalsColumn trendTitle="Test Trend" />)

    expect(screen.getByText('No image available')).toBeInTheDocument()
  })

  it('displays trend description when provided', () => {
    render(
      <SignalsColumn
        trendTitle="Test Trend"
        trendDescription="This is a detailed description of the trend"
      />
    )

    expect(screen.getByText('This is a detailed description of the trend')).toBeInTheDocument()
  })

  it('applies correct styling classes', () => {
    const { container } = render(<SignalsColumn trendTitle="Test Trend" />)

    const wrapper = container.firstChild as HTMLElement
    expect(wrapper.className).toMatch(/bg-white/)
    expect(wrapper.className).toMatch(/rounded-lg/)
    expect(wrapper.className).toMatch(/shadow-sm/)
  })
})

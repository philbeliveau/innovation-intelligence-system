import { render, screen } from '@testing-library/react'
import { SparksPreviewColumn } from '@/components/pipeline/SparksPreviewColumn'

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...props} />
  },
}))

describe('SparksPreviewColumn', () => {
  const mockSparks = [
    {
      number: 1,
      title: 'First Spark',
      summary: 'Summary of first spark',
      heroImageUrl: 'https://example.com/spark1.jpg',
    },
    {
      number: 2,
      title: 'Second Spark',
      summary: 'Summary of second spark',
    },
    {
      number: 3,
      title: 'Third Spark',
      summary: 'Summary of third spark',
    },
  ]

  it('renders header with icon and title', () => {
    render(<SparksPreviewColumn sparks={[]} isGenerating={false} />)

    expect(screen.getByText('Sparks')).toBeInTheDocument()
  })

  it('displays only first 2 sparks', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    expect(screen.getByText('First Spark')).toBeInTheDocument()
    expect(screen.getByText('Second Spark')).toBeInTheDocument()
    expect(screen.queryByText('Third Spark')).not.toBeInTheDocument()
  })

  it('displays number badges correctly', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('displays spark titles and summaries', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    expect(screen.getByText('First Spark')).toBeInTheDocument()
    expect(screen.getByText('Summary of first spark')).toBeInTheDocument()
    expect(screen.getByText('Second Spark')).toBeInTheDocument()
    expect(screen.getByText('Summary of second spark')).toBeInTheDocument()
  })

  it('displays hero image when provided', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    const image = screen.getByAltText('First Spark')
    expect(image).toBeInTheDocument()
    expect(image).toHaveAttribute('src', 'https://example.com/spark1.jpg')
  })

  it('shows placeholder when no hero image', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    expect(screen.getByText('No image')).toBeInTheDocument()
  })

  it('shows "More sparks generating..." when isGenerating is true', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={true} />)

    expect(screen.getByText('More sparks generating...')).toBeInTheDocument()
  })

  it('does not show generating text when isGenerating is false', () => {
    render(<SparksPreviewColumn sparks={mockSparks} isGenerating={false} />)

    expect(screen.queryByText('More sparks generating...')).not.toBeInTheDocument()
  })

  it('handles empty sparks array', () => {
    render(<SparksPreviewColumn sparks={[]} isGenerating={true} />)

    expect(screen.queryByText('First Spark')).not.toBeInTheDocument()
    expect(screen.getByText('More sparks generating...')).toBeInTheDocument()
  })
})

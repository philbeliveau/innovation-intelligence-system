import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import SparkCard from '@/components/pipeline/SparkCard'

const mockSpark = {
  id: 'spark-1',
  title: 'Test Spark Title',
  summary: 'This is a test summary for the spark card',
  content: '# Test Content\n\nFull markdown content here.',
}

describe('SparkCard', () => {
  it('renders spark data correctly', () => {
    const onClick = jest.fn()
    render(<SparkCard spark={mockSpark} number={1} onClick={onClick} />)

    expect(screen.getByText('Test Spark Title')).toBeInTheDocument()
    expect(screen.getByText('This is a test summary for the spark card')).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('calls onClick when card is clicked', () => {
    const onClick = jest.fn()
    render(<SparkCard spark={mockSpark} number={1} onClick={onClick} />)

    const card = screen.getByRole('button', { name: /view spark 1/i })
    fireEvent.click(card)

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('calls onClick when View button is clicked', () => {
    const onClick = jest.fn()
    render(<SparkCard spark={mockSpark} number={1} onClick={onClick} />)

    const viewButton = screen.getByRole('button', { name: /view details for/i })
    fireEvent.click(viewButton)

    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('shows gray placeholder when no hero image provided', () => {
    const onClick = jest.fn()
    const { container } = render(<SparkCard spark={mockSpark} number={1} onClick={onClick} />)

    const placeholder = container.querySelector('.bg-gray-200')
    expect(placeholder).toBeInTheDocument()
  })

  it('truncates long titles with line-clamp-2', () => {
    const longTitleSpark = {
      ...mockSpark,
      title:
        'This is a very long title that should be truncated after two lines to prevent layout issues',
    }
    const onClick = jest.fn()
    const { container } = render(<SparkCard spark={longTitleSpark} number={1} onClick={onClick} />)

    const title = container.querySelector('.line-clamp-2')
    expect(title).toBeInTheDocument()
  })

  it('truncates long summaries with line-clamp-4', () => {
    const longSummarySpark = {
      ...mockSpark,
      summary:
        'This is a very long summary that should be truncated after four lines to maintain consistent card heights and prevent excessive scrolling in the grid layout',
    }
    const onClick = jest.fn()
    const { container } = render(<SparkCard spark={longSummarySpark} number={1} onClick={onClick} />)

    const summary = container.querySelector('.line-clamp-4')
    expect(summary).toBeInTheDocument()
  })

  it('supports keyboard navigation', () => {
    const onClick = jest.fn()
    render(<SparkCard spark={mockSpark} number={1} onClick={onClick} />)

    const card = screen.getByRole('button', { name: /view spark 1/i })
    fireEvent.keyDown(card, { key: 'Enter' })

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})

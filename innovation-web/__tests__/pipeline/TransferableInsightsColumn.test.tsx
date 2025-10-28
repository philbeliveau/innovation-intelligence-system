import { render, screen, fireEvent } from '@testing-library/react'
import { TransferableInsightsColumn } from '@/components/pipeline/TransferableInsightsColumn'

describe('TransferableInsightsColumn', () => {
  const defaultProps = {
    coreMechanism: 'Core mechanism text',
    businessImpact: 'Business impact text',
    patternTransfersTo: ['Food & Beverage', 'Healthcare', 'Technology'],
    runId: 'test-run-123',
    onDownload: jest.fn(),
  }

  it('renders header with icon and title', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    expect(screen.getByText('Transferable Insights')).toBeInTheDocument()
  })

  it('displays all three sections', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    expect(screen.getByText('Core Mechanism')).toBeInTheDocument()
    expect(screen.getByText('Business Impact')).toBeInTheDocument()
    expect(screen.getByText('Pattern Transfers To')).toBeInTheDocument()
  })

  it('displays core mechanism content', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    expect(screen.getByText('Core mechanism text')).toBeInTheDocument()
  })

  it('displays business impact content', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    expect(screen.getByText('Business impact text')).toBeInTheDocument()
  })

  it('displays all industries in pattern transfers to list', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    expect(screen.getByText('Food & Beverage')).toBeInTheDocument()
    expect(screen.getByText('Healthcare')).toBeInTheDocument()
    expect(screen.getByText('Technology')).toBeInTheDocument()
  })

  it('renders download link', () => {
    render(<TransferableInsightsColumn {...defaultProps} />)

    const downloadButton = screen.getByText('View/download extraction report')
    expect(downloadButton).toBeInTheDocument()
  })

  it('calls onDownload when download link is clicked', () => {
    const onDownload = jest.fn()
    render(<TransferableInsightsColumn {...defaultProps} onDownload={onDownload} />)

    const downloadButton = screen.getByText('View/download extraction report')
    fireEvent.click(downloadButton)

    expect(onDownload).toHaveBeenCalledTimes(1)
  })

  it('applies scrollable container styles', () => {
    const { container } = render(<TransferableInsightsColumn {...defaultProps} />)

    const scrollableDiv = container.querySelector('.overflow-y-auto')
    expect(scrollableDiv).toBeInTheDocument()
    expect(scrollableDiv?.className).toMatch(/max-h-\[500px\]/)
  })
})

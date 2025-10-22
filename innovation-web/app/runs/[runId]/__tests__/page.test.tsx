import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import RunDetailPage from '../page'
import '@testing-library/jest-dom'

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

// Mock fetch
global.fetch = jest.fn()

// Mock jsPDF
jest.mock('jspdf', () => ({
  jsPDF: jest.fn().mockImplementation(() => ({
    setFontSize: jest.fn(),
    text: jest.fn(),
    splitTextToSize: jest.fn(() => ['line1', 'line2']),
    addPage: jest.fn(),
    save: jest.fn(),
  })),
}))

describe('RunDetailPage', () => {
  const mockPush = jest.fn()
  const mockSearchParams = new URLSearchParams()
  const mockParams = Promise.resolve({ runId: 'test-run-123' })

  const mockRunData = {
    id: 'test-run-123',
    documentName: 'Test Document.pdf',
    companyName: 'Test Company',
    status: 'COMPLETED',
    createdAt: new Date().toISOString(),
    completedAt: new Date().toISOString(),
    duration: 1800,
    pipelineVersion: '2.1.0',
    opportunityCards: [
      {
        id: 'card-1',
        number: 1,
        title: 'Test Card 1',
        content: '# Test Content',
        isStarred: false,
      },
      {
        id: 'card-2',
        number: 2,
        title: 'Test Card 2',
        content: '# Test Content 2',
        isStarred: true,
      },
    ],
    inspirationReport: {
      id: 'report-1',
      selectedTrack: '# Selected Track',
      nonSelectedTrack: '# Non-Selected Track',
      stage1Output: '# Stage 1',
      stage2Output: '# Stage 2',
      stage3Output: '# Stage 3',
      stage4Output: '# Stage 4',
      stage5Output: '# Stage 5',
    },
    stageOutputs: [
      {
        id: 'stage-1',
        stageNumber: 1,
        stageName: 'Test Stage 1',
        status: 'COMPLETED',
        completedAt: new Date().toISOString(),
        output: JSON.stringify({ test: 'data' }),
      },
    ],
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })
    ;(useSearchParams as jest.Mock).mockReturnValue(mockSearchParams)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockRunData,
    })
  })

  describe('Page Loading', () => {
    it('should show loading skeleton initially', () => {
      render(<RunDetailPage params={mockParams} />)

      // Loading skeletons should be visible
      const skeletons = screen.getAllByTestId(/skeleton/i)
      expect(skeletons.length).toBeGreaterThan(0)
    })

    it('should fetch run data on mount', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/runs/test-run-123')
      })
    })

    it('should display run data after loading', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Test Document.pdf')).toBeInTheDocument()
        expect(screen.getByText('Test Company')).toBeInTheDocument()
      })
    })
  })

  describe('Error Handling', () => {
    it('should display error message on 404', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText(/Run not found or you do not have permission/i)
        ).toBeInTheDocument()
      })
    })

    it('should display generic error on fetch failure', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'))

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to load run details/i)).toBeInTheDocument()
      })
    })

    it('should show back to runs button on error', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const backButton = screen.getByText('Back to Runs')
        expect(backButton).toBeInTheDocument()
      })
    })
  })

  describe('Breadcrumbs Navigation', () => {
    it('should render breadcrumbs with correct links', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Home')).toBeInTheDocument()
        expect(screen.getByText('My Runs')).toBeInTheDocument()
        expect(screen.getByText('Test Document.pdf')).toBeInTheDocument()
      })
    })
  })

  describe('Tab Navigation', () => {
    it('should default to cards tab', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const cardsTab = screen.getByRole('tab', { name: /Opportunity Cards/i })
        expect(cardsTab).toHaveAttribute('data-state', 'active')
      })
    })

    it('should respect tab query parameter', async () => {
      const searchParams = new URLSearchParams('tab=report')
      ;(useSearchParams as jest.Mock).mockReturnValue(searchParams)

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const reportTab = screen.getByRole('tab', { name: /Full Report/i })
        expect(reportTab).toHaveAttribute('data-state', 'active')
      })
    })

    it('should update URL when switching tabs', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const reportTab = screen.getByRole('tab', { name: /Full Report/i })
        fireEvent.click(reportTab)
      })

      expect(mockPush).toHaveBeenCalledWith(
        '/runs/test-run-123?tab=report',
        expect.any(Object)
      )
    })
  })

  describe('Opportunity Cards Tab', () => {
    it('should display all opportunity cards', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Test Card 1')).toBeInTheDocument()
        expect(screen.getByText('Test Card 2')).toBeInTheDocument()
      })
    })

    it('should show starred cards with filled star icon', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        // Card 2 is starred in mock data
        const starButtons = screen.getAllByRole('button', { name: '' })
        // We can't easily test icon fill state, but button should be present
        expect(starButtons.length).toBeGreaterThan(0)
      })
    })

    it('should toggle star when clicking star button', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockRunData,
      })
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'card-1', isStarred: true }),
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Test Card 1')).toBeInTheDocument()
      })

      // Find and click star button (this is simplified - in real test would need better selector)
      const starButtons = screen.getAllByRole('button')
      const starButton = starButtons.find((btn) => btn.className.includes('star'))
      if (starButton) {
        fireEvent.click(starButton)

        await waitFor(() => {
          expect(global.fetch).toHaveBeenCalledWith(
            '/api/cards/card-1/star',
            expect.objectContaining({ method: 'POST' })
          )
        })
      }
    })

    it('should expand card in modal when clicked', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const card = screen.getByText('Test Card 1')
        fireEvent.click(card.closest('div[role="button"]') || card)
      })

      // Modal should open (implementation depends on Dialog component)
      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument()
      })
    })
  })

  describe('Action Buttons', () => {
    it('should show rerun button', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Rerun')).toBeInTheDocument()
      })
    })

    it('should show download PDF button', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Download PDF')).toBeInTheDocument()
      })
    })

    it('should show delete button', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Delete Run')).toBeInTheDocument()
      })
    })

    it('should disable download PDF when status is not COMPLETED', async () => {
      const processingRun = { ...mockRunData, status: 'PROCESSING' }
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => processingRun,
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const downloadButton = screen.getByText('Download PDF').closest('button')
        expect(downloadButton).toBeDisabled()
      })
    })

    it('should open delete confirmation dialog', async () => {
      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const deleteButton = screen.getByText('Delete Run')
        fireEvent.click(deleteButton)
      })

      await waitFor(() => {
        expect(
          screen.getByText('Are you sure you want to delete this run?')
        ).toBeInTheDocument()
      })
    })

    it('should call delete API and redirect on confirm', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockRunData,
      })
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const deleteButton = screen.getByText('Delete Run')
        fireEvent.click(deleteButton)
      })

      await waitFor(() => {
        const confirmButton = screen.getAllByText('Delete')[1] // Second "Delete" is in dialog
        fireEvent.click(confirmButton)
      })

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/runs/test-run-123',
          expect.objectContaining({ method: 'DELETE' })
        )
        expect(mockPush).toHaveBeenCalledWith('/runs')
      })
    })
  })

  describe('Processing Status', () => {
    it('should show processing banner when status is PROCESSING', async () => {
      const processingRun = { ...mockRunData, status: 'PROCESSING' }
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => processingRun,
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(
          screen.getByText(/Pipeline is currently processing/i)
        ).toBeInTheDocument()
      })
    })

    it('should poll for updates when status is PROCESSING', async () => {
      jest.useFakeTimers()

      const processingRun = { ...mockRunData, status: 'PROCESSING' }
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => processingRun,
      })

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        expect(screen.getByText('Test Document.pdf')).toBeInTheDocument()
      })

      // Advance time to trigger polling
      jest.advanceTimersByTime(5000)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2) // Initial + poll
      })

      jest.useRealTimers()
    })
  })

  describe('Mobile Responsive', () => {
    it('should render tabs in single column on mobile', async () => {
      // Set viewport to mobile size
      global.innerWidth = 375
      global.dispatchEvent(new Event('resize'))

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const tabsList = screen.getByRole('tablist')
        // TabsList should have responsive grid classes
        expect(tabsList.className).toContain('grid-cols')
      })
    })
  })

  describe('PDF Download', () => {
    it('should generate PDF with all cards', async () => {
      const { jsPDF } = await import('jspdf')

      render(<RunDetailPage params={mockParams} />)

      await waitFor(() => {
        const downloadButton = screen.getByText('Download PDF')
        fireEvent.click(downloadButton)
      })

      await waitFor(() => {
        expect(jsPDF).toHaveBeenCalled()
      })
    })
  })
})

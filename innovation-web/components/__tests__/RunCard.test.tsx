import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import RunCard from '../RunCard'
import { SidebarRun } from '@/app/api/runs/route'
import '@testing-library/jest-dom'

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// Mock fetch
global.fetch = jest.fn()

describe('RunCard', () => {
  const mockRouter = {
    push: jest.fn(),
  }

  const mockRun: SidebarRun = {
    id: 'test-run-1',
    documentName: 'Test Document.pdf',
    companyName: 'Test Company',
    status: 'COMPLETED',
    cardCount: 5,
    createdAt: new Date('2024-01-15').toISOString(),
  }

  const mockOnDelete = jest.fn()
  const mockOnRerun = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ success: true }),
    })
  })

  describe('Rendering', () => {
    it('should render run information correctly', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      expect(screen.getByText('Test Document.pdf')).toBeInTheDocument()
      expect(screen.getByText('Test Company')).toBeInTheDocument()
      expect(screen.getByText('5 cards')).toBeInTheDocument()
    })

    it('should display status badge', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      expect(screen.getByText('Completed')).toBeInTheDocument()
    })

    it('should show relative date', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      // Should show a date (exact format may vary)
      const dateElements = screen.getAllByText(/ago|Jan|2024/i)
      expect(dateElements.length).toBeGreaterThan(0)
    })
  })

  describe('Card Actions', () => {
    it('should navigate to detail page when View clicked', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      const viewButton = screen.getByText('View')
      fireEvent.click(viewButton)

      expect(mockRouter.push).toHaveBeenCalledWith('/runs/test-run-1')
    })

    it('should show delete confirmation dialog when Delete clicked', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      const deleteButton = screen.getByRole('button', { name: /trash/i })
      fireEvent.click(deleteButton)

      expect(screen.getByText('Delete Pipeline Run')).toBeInTheDocument()
      expect(
        screen.getByText(/Are you sure you want to delete this run/i)
      ).toBeInTheDocument()
    })

    it('should show rerun confirmation dialog when Rerun clicked', () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      const rerunButton = screen.getByText('Rerun')
      fireEvent.click(rerunButton)

      expect(screen.getByText('Rerun Pipeline')).toBeInTheDocument()
      expect(
        screen.getByText(/This will create a new pipeline run/i)
      ).toBeInTheDocument()
    })
  })

  describe('Delete Flow', () => {
    it('should call API and trigger onDelete when confirmed', async () => {
      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      // Open delete dialog
      const deleteButton = screen.getByRole('button', { name: /trash/i })
      fireEvent.click(deleteButton)

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /^Delete$/i })
      fireEvent.click(confirmButton)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/runs/test-run-1',
          expect.objectContaining({ method: 'DELETE' })
        )
        expect(mockOnDelete).toHaveBeenCalledWith('test-run-1')
      })
    })

    it('should handle delete failure gracefully', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
      })

      const alertSpy = jest.spyOn(window, 'alert').mockImplementation()

      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      // Open and confirm delete
      const deleteButton = screen.getByRole('button', { name: /trash/i })
      fireEvent.click(deleteButton)

      const confirmButton = screen.getByRole('button', { name: /^Delete$/i })
      fireEvent.click(confirmButton)

      await waitFor(() => {
        expect(alertSpy).toHaveBeenCalledWith(
          expect.stringContaining('Failed to delete')
        )
      })

      alertSpy.mockRestore()
    })
  })

  describe('Rerun Flow', () => {
    it('should call API and navigate when rerun confirmed', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, newRunId: 'new-run-123' }),
      })

      render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      // Open rerun dialog
      const rerunButton = screen.getByText('Rerun')
      fireEvent.click(rerunButton)

      // Confirm rerun
      const confirmButton = screen.getByText('Start Rerun')
      fireEvent.click(confirmButton)

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          '/api/runs/test-run-1/rerun',
          expect.objectContaining({ method: 'POST' })
        )
        expect(mockOnRerun).toHaveBeenCalledWith('new-run-123')
        expect(mockRouter.push).toHaveBeenCalledWith('/pipeline/new-run-123')
      })
    })
  })

  describe('Hover Effects', () => {
    it('should apply brutalist styling', () => {
      const { container } = render(
        <RunCard run={mockRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      const card = container.querySelector('[class*="border"]')
      expect(card).toHaveClass('border-[5px]')
      expect(card).toHaveClass('border-black')
    })
  })

  describe('Status Variations', () => {
    it('should render PROCESSING status correctly', () => {
      const processingRun = { ...mockRun, status: 'PROCESSING' as const }
      render(
        <RunCard
          run={processingRun}
          onDelete={mockOnDelete}
          onRerun={mockOnRerun}
        />
      )

      expect(screen.getByText('Processing')).toBeInTheDocument()
    })

    it('should render FAILED status correctly', () => {
      const failedRun = { ...mockRun, status: 'FAILED' as const }
      render(
        <RunCard run={failedRun} onDelete={mockOnDelete} onRerun={mockOnRerun} />
      )

      expect(screen.getByText('Failed')).toBeInTheDocument()
    })
  })
})

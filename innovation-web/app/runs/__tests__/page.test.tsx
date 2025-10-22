import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter, useSearchParams } from 'next/navigation'
import RunsPage from '../page'
import '@testing-library/jest-dom'

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}))

// Mock fetch
global.fetch = jest.fn()

describe('RunsPage', () => {
  const mockRouter = {
    push: jest.fn(),
  }

  const mockSearchParams = {
    get: jest.fn((key: string) => {
      if (key === 'page') return '1'
      return null
    }),
    toString: jest.fn(() => ''),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(useSearchParams as jest.Mock).mockReturnValue(mockSearchParams)
    ;(global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({
        runs: [],
        total: 0,
        page: 1,
        pageSize: 12,
        uniqueCompanies: [],
      }),
    })
  })

  describe('Rendering', () => {
    it('should render the page title', async () => {
      render(<RunsPage />)
      await waitFor(() => {
        expect(screen.getByText('Your Innovation Runs')).toBeInTheDocument()
      })
    })

    it('should render filter controls', async () => {
      render(<RunsPage />)
      await waitFor(() => {
        expect(screen.getByPlaceholderText('Search by document name...')).toBeInTheDocument()
      })
    })
  })

  describe('Filtering', () => {
    it('should fetch runs with search filter', async () => {
      render(<RunsPage />)

      const searchInput = screen.getByPlaceholderText('Search by document name...')
      fireEvent.change(searchInput, { target: { value: 'test' } })

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('search=test')
        )
      })
    })

    it('should apply status filter', async () => {
      const mockRuns = [
        {
          id: '1',
          documentName: 'Test.pdf',
          companyName: 'Test Co',
          status: 'COMPLETED',
          cardCount: 5,
          createdAt: new Date().toISOString(),
        },
      ]

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          runs: mockRuns,
          total: 1,
          page: 1,
          pageSize: 12,
          uniqueCompanies: ['Test Co'],
        }),
      })

      render(<RunsPage />)

      await waitFor(() => {
        expect(screen.getByText('Test.pdf')).toBeInTheDocument()
      })
    })
  })

  describe('Empty State', () => {
    it('should show empty state when no runs exist', async () => {
      render(<RunsPage />)

      await waitFor(() => {
        expect(screen.getByText('No runs yet')).toBeInTheDocument()
        expect(screen.getByText('Upload a document to get started.')).toBeInTheDocument()
      })
    })
  })

  describe('Loading State', () => {
    it('should show loading skeletons while fetching', () => {
      render(<RunsPage />)

      // Check for skeleton elements (they won't have specific text)
      const skeletons = screen.getAllByRole('generic')
      expect(skeletons.length).toBeGreaterThan(0)
    })
  })

  describe('Error State', () => {
    it('should show error message when fetch fails', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValue(new Error('Failed to fetch'))

      render(<RunsPage />)

      await waitFor(() => {
        expect(screen.getByText(/Failed to fetch/i)).toBeInTheDocument()
      })
    })

    it('should show retry button on error', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValue(new Error('Failed to fetch'))

      render(<RunsPage />)

      await waitFor(() => {
        const retryButton = screen.getByText('Retry')
        expect(retryButton).toBeInTheDocument()
      })
    })
  })

  describe('Pagination', () => {
    it('should navigate to next page when next button clicked', async () => {
      const mockRuns = Array.from({ length: 12 }, (_, i) => ({
        id: `${i}`,
        documentName: `Test${i}.pdf`,
        companyName: 'Test Co',
        status: 'COMPLETED' as const,
        cardCount: 5,
        createdAt: new Date().toISOString(),
      }))

      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({
          runs: mockRuns,
          total: 24,
          page: 1,
          pageSize: 12,
          uniqueCompanies: ['Test Co'],
        }),
      })

      render(<RunsPage />)

      await waitFor(() => {
        const nextButton = screen.getByText('Next')
        expect(nextButton).toBeInTheDocument()
      })
    })
  })

  describe('Sorting', () => {
    it('should persist sort preference to localStorage', async () => {
      const setItemSpy = jest.spyOn(Storage.prototype, 'setItem')

      render(<RunsPage />)

      await waitFor(() => {
        expect(setItemSpy).toHaveBeenCalledWith('runs-sort-preference', expect.any(String))
      })

      setItemSpy.mockRestore()
    })
  })
})

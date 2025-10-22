import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { useRouter, usePathname } from 'next/navigation'
import { LeftSidebar } from '../LeftSidebar'
import { useRuns } from '@/lib/use-runs'

// Mock Next.js navigation hooks
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}))

// Mock Clerk authentication
jest.mock('@clerk/nextjs', () => ({
  SignInButton: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SignedIn: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SignedOut: () => null,
  UserButton: () => <div>User Button</div>,
}))

// Mock useRuns hook
jest.mock('@/lib/use-runs')

// Mock formatRelativeTime
jest.mock('@/lib/format-relative-time', () => ({
  formatRelativeTime: (date: string) => {
    const d = new Date(date)
    return `${d.getHours()}h ago`
  },
}))

const mockRouterPush = jest.fn()
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>
const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>
const mockUseRuns = useRuns as jest.MockedFunction<typeof useRuns>

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRouter = any

describe('LeftSidebar - My Runs Section', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockRouterPush,
    } as AnyRouter)
    mockUsePathname.mockReturnValue('/')
  })

  it('renders "My Runs" section when signed in', () => {
    mockUseRuns.mockReturnValue({
      runs: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(screen.getByText('My Runs')).toBeInTheDocument()
  })

  it('displays loading skeleton while fetching runs', () => {
    mockUseRuns.mockReturnValue({
      runs: [],
      loading: true,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    const skeletons = screen.getAllByRole('generic').filter(el =>
      el.className.includes('animate-pulse')
    )
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it('displays error message when API call fails', () => {
    const errorMessage = 'Failed to fetch runs'
    mockUseRuns.mockReturnValue({
      runs: [],
      loading: false,
      error: errorMessage,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(screen.getByText(errorMessage)).toBeInTheDocument()
  })

  it('displays "No runs yet" when runs array is empty', () => {
    mockUseRuns.mockReturnValue({
      runs: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(screen.getByText('No runs yet')).toBeInTheDocument()
  })

  it('renders run items with correct information', () => {
    const mockRuns = [
      {
        id: 'run-1',
        documentName: 'Trend Report Q4 2024.pdf',
        companyName: 'Lactalis Canada',
        createdAt: new Date().toISOString(),
        status: 'COMPLETED' as const,
        cardCount: 12,
      },
      {
        id: 'run-2',
        documentName: 'Innovation Brief.pdf',
        companyName: 'KIND Snacks',
        createdAt: new Date().toISOString(),
        status: 'PROCESSING' as const,
        cardCount: 0,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(screen.getByText(/Trend Report Q4/)).toBeInTheDocument()
    expect(screen.getByText('Lactalis Canada')).toBeInTheDocument()
    expect(screen.getByText('12 cards')).toBeInTheDocument()

    expect(screen.getByText(/Innovation Brief/)).toBeInTheDocument()
    expect(screen.getByText('KIND Snacks')).toBeInTheDocument()
  })

  it('displays correct status badges', () => {
    const mockRuns = [
      {
        id: 'run-1',
        documentName: 'Test.pdf',
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'COMPLETED' as const,
        cardCount: 5,
      },
      {
        id: 'run-2',
        documentName: 'Test2.pdf',
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'FAILED' as const,
        cardCount: 0,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    // Check for status emoji
    expect(screen.getByText('✅')).toBeInTheDocument()
    expect(screen.getByText('❌')).toBeInTheDocument()
  })

  it('navigates to run detail page when run is clicked', async () => {
    const mockRuns = [
      {
        id: 'run-123',
        documentName: 'Test.pdf',
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'COMPLETED' as const,
        cardCount: 5,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    const runButton = screen.getByTitle(/Test.pdf - Test Co/)
    fireEvent.click(runButton)

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/runs/run-123')
    })
  })

  it('navigates to runs page when "View All Runs" is clicked', async () => {
    const mockRuns = [
      {
        id: 'run-1',
        documentName: 'Test.pdf',
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'COMPLETED' as const,
        cardCount: 5,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    const viewAllButton = screen.getByText('View All Runs →')
    fireEvent.click(viewAllButton)

    await waitFor(() => {
      expect(mockRouterPush).toHaveBeenCalledWith('/runs')
    })
  })

  it('enables polling when on pipeline viewer page', () => {
    mockUsePathname.mockReturnValue('/pipeline/run-123')

    mockUseRuns.mockReturnValue({
      runs: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(mockUseRuns).toHaveBeenCalledWith({
      pageSize: 5,
      pollingInterval: 10000,
      enabled: true,
    })
  })

  it('disables polling when not on pipeline viewer page', () => {
    mockUsePathname.mockReturnValue('/upload')

    mockUseRuns.mockReturnValue({
      runs: [],
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    expect(mockUseRuns).toHaveBeenCalledWith({
      pageSize: 5,
      pollingInterval: 10000,
      enabled: false,
    })
  })

  it('truncates long document names', () => {
    const longName = 'This is a very long document name that should be truncated.pdf'
    const mockRuns = [
      {
        id: 'run-1',
        documentName: longName,
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'COMPLETED' as const,
        cardCount: 5,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    render(<LeftSidebar />)

    // Should show truncated version (20 chars + ...)
    const truncatedText = screen.getByText(/This is a very long/)
    expect(truncatedText.textContent).toContain('...')
  })

  it('displays animated spinner for PROCESSING status', () => {
    const mockRuns = [
      {
        id: 'run-1',
        documentName: 'Test.pdf',
        companyName: 'Test Co',
        createdAt: new Date().toISOString(),
        status: 'PROCESSING' as const,
        cardCount: 0,
      },
    ]

    mockUseRuns.mockReturnValue({
      runs: mockRuns,
      loading: false,
      error: null,
      refetch: jest.fn(),
    })

    const { container } = render(<LeftSidebar />)

    const spinner = container.querySelector('.animate-spin')
    expect(spinner).toBeInTheDocument()
  })
})

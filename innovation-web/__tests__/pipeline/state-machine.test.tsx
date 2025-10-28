import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import PipelineStateMachine from '@/components/pipeline/PipelineStateMachine'
import { PipelineData, PipelineStatus } from '@/types/pipeline-state'

// Mock react-markdown to avoid ES module issues in tests
jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }: { children: string }) => <div>{children}</div>
}))

jest.mock('remark-gfm', () => ({
  __esModule: true,
  default: () => {}
}))

jest.mock('rehype-sanitize', () => ({
  __esModule: true,
  default: () => {}
}))

// Mock animation hooks
jest.mock('@/hooks/useReducedMotion', () => ({
  useReducedMotion: () => false
}))

jest.mock('@/hooks/useWillChange', () => ({
  useWillChange: () => ({ current: null })
}))

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
  usePathname: () => '/pipeline/test-run-123',
}))

// Mock pipeline data
const createMockPipelineData = (overrides?: Partial<PipelineData>): PipelineData => ({
  runId: 'test-run-123',
  stages: [],
  opportunityCards: [
    {
      id: '1',
      number: 1,
      title: 'Test Opportunity 1',
      summary: 'Test summary 1',
      markdown: 'Test markdown content 1',
    },
    {
      id: '2',
      number: 2,
      title: 'Test Opportunity 2',
      summary: 'Test summary 2',
      markdown: 'Test markdown content 2',
    },
  ],
  brandName: 'Test Brand',
  ...overrides,
})

describe('PipelineStateMachine', () => {
  describe('State 1: Extraction Animation', () => {
    it('should render State 1 when currentStage=1 and status=PROCESSING', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      expect(screen.getByTestId('state-1')).toBeInTheDocument()
      expect(screen.getByText(/Stage 1: Extracting Inspiration Tracks/i)).toBeInTheDocument()
      expect(screen.getByText(/Analyzing document for innovation signals/i)).toBeInTheDocument()
    })
  })

  describe('State 2: Three-Column Progress', () => {
    it('should render State 2 when currentStage=2 and status=PROCESSING', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={2}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      expect(screen.getByTestId('state-2')).toBeInTheDocument()
      expect(screen.getByText('Signals')).toBeInTheDocument()
      expect(screen.getByText('Transferable Insights')).toBeInTheDocument()
      expect(screen.getByText('Sparks')).toBeInTheDocument()
    })

    it('should render State 2 when currentStage=3 and status=PROCESSING', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={3}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      expect(screen.getByTestId('state-2')).toBeInTheDocument()
    })

    it('should render State 2 when currentStage=5 and status=PROCESSING', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      expect(screen.getByTestId('state-2')).toBeInTheDocument()
    })
  })

  describe('State 3: Sparks Grid View', () => {
    it('should render State 3 when status=COMPLETED and selectedCardId=null', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId={null}
        />
      )

      expect(screen.getByTestId('state-3')).toBeInTheDocument()
      expect(screen.getByText('Innovation Sparks')).toBeInTheDocument()
      expect(screen.getByText('Download All')).toBeInTheDocument()
      expect(screen.getByText('New Pipeline')).toBeInTheDocument()
    })

    it('should render State 3 when status=COMPLETED and selectedCardId=undefined', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
        />
      )

      expect(screen.getByTestId('state-3')).toBeInTheDocument()
    })

    it('should display opportunity cards in grid', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId={null}
        />
      )

      expect(screen.getByText('Test Opportunity 1')).toBeInTheDocument()
      expect(screen.getByText('Test Opportunity 2')).toBeInTheDocument()
      expect(screen.getByText('Test summary 1')).toBeInTheDocument()
    })

    it('should show empty state when no opportunity cards', () => {
      const mockData = createMockPipelineData({ opportunityCards: [] })
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId={null}
        />
      )

      expect(screen.getByText('No opportunity cards generated yet.')).toBeInTheDocument()
    })
  })

  describe('State 4: Card Detail View', () => {
    it('should render State 4 when status=COMPLETED and selectedCardId is provided', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId="1"
        />
      )

      expect(screen.getByTestId('state-4')).toBeInTheDocument()
      expect(screen.getByText('← Back to Grid')).toBeInTheDocument()
    })

    it('should display selected card details', () => {
      const mockData = createMockPipelineData()
      render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId="1"
        />
      )

      // Use getAllByText since title appears in both sidebar and detail view
      expect(screen.getAllByText('Test Opportunity 1').length).toBeGreaterThan(0)
      expect(screen.getByText('Test markdown content 1')).toBeInTheDocument()
      expect(screen.getByText('Download PDF')).toBeInTheDocument()
    })
  })

  describe('Responsive Layout Classes', () => {
    it('should apply mobile-first responsive classes to State 1', () => {
      const mockData = createMockPipelineData()
      const { container } = render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      const state1 = container.querySelector('[data-testid="state-1"]')
      expect(state1).toHaveClass('flex', 'flex-col', 'space-y-4')
    })

    it('should apply responsive grid classes to State 2', () => {
      const mockData = createMockPipelineData()
      const { container } = render(
        <PipelineStateMachine
          currentStage={2}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      const state2 = container.querySelector('[data-testid="state-2"]')
      expect(state2).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-3', 'gap-4')
    })

    it('should apply responsive grid classes to State 3', () => {
      const mockData = createMockPipelineData()
      const { container } = render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
        />
      )

      // State 3 grid is inside data-testid="state-3"
      const gridContainer = screen.getByTestId('state-3').querySelector('.grid')
      expect(gridContainer).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-2', 'gap-4')
    })

    it('should apply responsive grid classes to State 4', () => {
      const mockData = createMockPipelineData()
      const { container } = render(
        <PipelineStateMachine
          currentStage={5}
          status="COMPLETED"
          pipelineData={mockData}
          selectedCardId="1"
        />
      )

      const state4 = container.querySelector('[data-testid="state-4"]')
      expect(state4).toHaveClass('grid', 'grid-cols-1', 'lg:grid-cols-12', 'gap-4')
    })
  })

  describe('CSS Transitions', () => {
    it('should apply transition classes to root container', () => {
      const mockData = createMockPipelineData()
      const { container } = render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockData}
        />
      )

      const rootDiv = container.firstChild
      expect(rootDiv).toHaveClass('transition-all', 'duration-300', 'ease-in-out')
    })
  })
})

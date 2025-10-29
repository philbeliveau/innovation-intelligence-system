/**
 * Tests for PipelineStateMachine component
 * Story 10.7: Dual-mode pipeline viewing (live vs retrospective)
 */

import { render, screen } from '@testing-library/react'
import PipelineStateMachine from '@/components/pipeline/PipelineStateMachine'
import { PipelineData, PipelineStatus } from '@/types/pipeline-state'

// Mock child components
jest.mock('@/components/pipeline/ExtractionAnimation', () => ({
  __esModule: true,
  default: () => <div data-testid="extraction-animation">Extraction Animation</div>,
}))

jest.mock('@/components/pipeline/WorkflowIllustration', () => ({
  __esModule: true,
  default: () => <div data-testid="workflow-illustration">Workflow Illustration</div>,
}))

jest.mock('@/components/pipeline/ThreeColumnLayout', () => ({
  ThreeColumnLayout: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="three-column-layout">{children}</div>
  ),
}))

jest.mock('@/components/pipeline/SignalsColumn', () => ({
  SignalsColumn: () => <div data-testid="signals-column">Signals</div>,
}))

jest.mock('@/components/pipeline/TransferableInsightsColumn', () => ({
  TransferableInsightsColumn: () => <div data-testid="insights-column">Insights</div>,
}))

jest.mock('@/components/pipeline/SparksPreviewColumn', () => ({
  SparksPreviewColumn: () => <div data-testid="sparks-column">Sparks</div>,
}))

jest.mock('@/components/pipeline/LoadingSkeletons', () => ({
  SignalsColumnSkeleton: () => <div data-testid="signals-skeleton">Loading...</div>,
  TransferableInsightsColumnSkeleton: () => <div data-testid="insights-skeleton">Loading...</div>,
  SparksPreviewColumnSkeleton: () => <div data-testid="sparks-skeleton">Loading...</div>,
}))

jest.mock('@/components/pipeline/ModeIndicator', () => ({
  ModeIndicator: ({ mode, completedAt }: { mode: string; completedAt?: string | null }) => (
    <div data-testid="mode-indicator" data-mode={mode} data-completed-at={completedAt}>
      {mode === 'live' ? 'Live Pipeline Running' : 'Completed Analysis'}
    </div>
  ),
}))

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

jest.mock('@/components/pipeline/IconNavigation', () => ({
  __esModule: true,
  default: () => <div data-testid="icon-navigation">Icon Navigation</div>,
}))

jest.mock('@/components/pipeline/SparksGrid', () => ({
  __esModule: true,
  default: () => <div data-testid="sparks-grid">Sparks Grid</div>,
}))

jest.mock('@/components/pipeline/ActionBar', () => ({
  __esModule: true,
  default: () => <div data-testid="action-bar">Action Bar</div>,
}))

jest.mock('@/components/pipeline/CollapsedSidebar', () => ({
  __esModule: true,
  default: () => <div data-testid="collapsed-sidebar">Collapsed Sidebar</div>,
}))

jest.mock('@/components/pipeline/ExpandedSparkDetail', () => ({
  __esModule: true,
  default: () => <div data-testid="expanded-spark-detail">Expanded Spark Detail</div>,
}))

jest.mock('@/components/pipeline/MobileSparkNavigationMenu', () => ({
  __esModule: true,
  default: () => <div data-testid="mobile-menu">Mobile Menu</div>,
}))

jest.mock('@/components/animations/FadeTransition', () => ({
  FadeTransition: ({ children, isVisible }: { children: React.ReactNode; isVisible: boolean }) => (
    isVisible ? <div>{children}</div> : null
  ),
}))

jest.mock('@/components/animations/StateAnnouncer', () => ({
  StateAnnouncer: () => null,
}))

describe('PipelineStateMachine - Dual Mode Support', () => {
  const basePipelineData: PipelineData = {
    runId: 'test-run-123',
    stages: [
      { stageNumber: 1, status: 'completed', completedAt: '2025-01-29T12:00:00Z' },
      { stageNumber: 2, status: 'completed' },
      { stageNumber: 3, status: 'completed' },
      { stageNumber: 4, status: 'completed' },
      { stageNumber: 5, status: 'completed', completedAt: '2025-01-29T12:30:00Z' },
    ],
    opportunityCards: [],
  }

  describe('Mode Detection', () => {
    it('detects live mode when status is PROCESSING', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status={'PROCESSING' as PipelineStatus}
          pipelineData={basePipelineData}
        />
      )

      const modeIndicator = screen.getByTestId('mode-indicator')
      expect(modeIndicator).toHaveAttribute('data-mode', 'live')
      expect(modeIndicator).toHaveTextContent('Live Pipeline Running')
    })

    it('detects retrospective mode when status is COMPLETED with stage outputs', () => {
      const pipelineDataWithOutputs = {
        ...basePipelineData,
        stage1Output: {
          extractedText: 'test',
          mechanisms: [],
        },
      }

      render(
        <PipelineStateMachine
          currentStage={5}
          status={'COMPLETED' as PipelineStatus}
          pipelineData={pipelineDataWithOutputs}
        />
      )

      const modeIndicator = screen.getByTestId('mode-indicator')
      expect(modeIndicator).toHaveAttribute('data-mode', 'retrospective')
      expect(modeIndicator).toHaveTextContent('Completed Analysis')
    })

    it('shows live mode when COMPLETED but no stage outputs (old runs)', () => {
      render(
        <PipelineStateMachine
          currentStage={5}
          status={'COMPLETED' as PipelineStatus}
          pipelineData={basePipelineData}
        />
      )

      const modeIndicator = screen.getByTestId('mode-indicator')
      expect(modeIndicator).toHaveAttribute('data-mode', 'live')
    })
  })

  describe('Mode Indicator Display', () => {
    it('shows completion timestamp in retrospective mode', () => {
      const pipelineDataWithOutputs = {
        ...basePipelineData,
        stage1Output: {
          extractedText: 'test',
          mechanisms: [],
        },
      }

      render(
        <PipelineStateMachine
          currentStage={5}
          status={'COMPLETED' as PipelineStatus}
          pipelineData={pipelineDataWithOutputs}
        />
      )

      const modeIndicator = screen.getByTestId('mode-indicator')
      expect(modeIndicator).toHaveAttribute('data-completed-at', '2025-01-29T12:30:00Z')
    })

    it('mode indicator still receives timestamp even in live mode', () => {
      // Note: Timestamp is derived from stage 5's completedAt
      // In a truly live run, stage 5 wouldn't have completedAt yet
      const liveRunData = {
        ...basePipelineData,
        stages: [
          { stageNumber: 1, status: 'processing' as const },
          { stageNumber: 2, status: 'pending' as const },
          { stageNumber: 3, status: 'pending' as const },
          { stageNumber: 4, status: 'pending' as const },
          { stageNumber: 5, status: 'pending' as const },
        ],
      }

      render(
        <PipelineStateMachine
          currentStage={1}
          status={'PROCESSING' as PipelineStatus}
          pipelineData={liveRunData}
        />
      )

      const modeIndicator = screen.getByTestId('mode-indicator')
      expect(modeIndicator).toHaveAttribute('data-mode', 'live')
      // In live mode with no completed stage 5, completedAt should be undefined (null in DOM)
      expect(modeIndicator.getAttribute('data-completed-at')).toBeNull()
    })
  })

  describe('State 1 - Extraction Animation', () => {
    it('renders State 1 when currentStage is 1', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status={'PROCESSING' as PipelineStatus}
          pipelineData={basePipelineData}
        />
      )

      expect(screen.getByTestId('state-1')).toBeInTheDocument()
      expect(screen.getByTestId('extraction-animation')).toBeInTheDocument()
      expect(screen.getByTestId('workflow-illustration')).toBeInTheDocument()
    })
  })

  describe('State 2 - Three Column Layout', () => {
    it('renders State 2 when currentStage is 2 or higher', () => {
      render(
        <PipelineStateMachine
          currentStage={2}
          status={'PROCESSING' as PipelineStatus}
          pipelineData={{
            ...basePipelineData,
            stages: [
              { stageNumber: 1, status: 'completed', output: '{"extractedText":"test","mechanisms":[]}' },
              { stageNumber: 2, status: 'processing' },
            ],
          }}
        />
      )

      expect(screen.getByTestId('state-2')).toBeInTheDocument()
      expect(screen.getByTestId('three-column-layout')).toBeInTheDocument()
    })

    it('renders skeletons when stage 1 has no output', () => {
      render(
        <PipelineStateMachine
          currentStage={2}
          status={'PROCESSING' as PipelineStatus}
          pipelineData={{
            ...basePipelineData,
            stages: [
              { stageNumber: 1, status: 'processing' },
              { stageNumber: 2, status: 'pending' },
            ],
          }}
        />
      )

      expect(screen.getByTestId('signals-skeleton')).toBeInTheDocument()
      expect(screen.getByTestId('insights-skeleton')).toBeInTheDocument()
    })
  })
})

/**
 * State 1 Integration Tests
 * Tests State 1 rendering in PipelineStateMachine
 */

import { render, screen } from '@testing-library/react'
import PipelineStateMachine from '@/components/pipeline/PipelineStateMachine'
import { PipelineData } from '@/types/pipeline-state'

const mockPipelineData: PipelineData = {
  runId: 'test-run-123',
  stages: [
    {
      stageNumber: 1,
      status: 'processing',
      output: undefined,
      completedAt: undefined,
    },
  ],
  opportunityCards: [],
  brandName: 'Test Brand',
}

describe('PipelineStateMachine - State 1 Integration', () => {
  describe('State 1 Activation', () => {
    it('should render State 1 when currentStage is 1 and status is PROCESSING', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const state1 = screen.getByTestId('state-1')
      expect(state1).toBeInTheDocument()
    })

    it('should not render State 1 when currentStage is 2', () => {
      render(
        <PipelineStateMachine
          currentStage={2}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      expect(screen.queryByTestId('state-1')).not.toBeInTheDocument()
    })

    it('should not render State 1 when status is COMPLETED', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="COMPLETED"
          pipelineData={{
            ...mockPipelineData,
            stages: [
              {
                stageNumber: 1,
                status: 'completed',
                output: '{}',
                completedAt: new Date().toISOString(),
              },
            ],
          }}
        />
      )

      expect(screen.queryByTestId('state-1')).not.toBeInTheDocument()
    })
  })

  describe('State 1 Layout', () => {
    it('should render two-column layout on desktop', () => {
      const { container } = render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const state1 = screen.getByTestId('state-1')
      expect(state1).toHaveClass('grid', 'grid-cols-1', 'lg:grid-cols-2')
    })

    it('should have gap between columns', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const state1 = screen.getByTestId('state-1')
      expect(state1).toHaveClass('gap-6')
    })

    it('should render two boxes', () => {
      const { container } = render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const boxes = container.querySelectorAll('[data-testid="state-1"] > div')
      expect(boxes).toHaveLength(2)
    })

    it('should apply minimum height to boxes', () => {
      const { container } = render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const boxes = container.querySelectorAll('[data-testid="state-1"] > div')
      boxes.forEach((box) => {
        expect(box).toHaveClass('min-h-[400px]')
      })
    })
  })

  describe('State 1 Components', () => {
    it('should render ExtractionAnimation component', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      expect(
        screen.getByText(/Extracting transferable insights from your document/i)
      ).toBeInTheDocument()
    })

    it('should render WorkflowIllustration component', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      expect(screen.getByText(/Understanding the core transferable pattern/i)).toBeInTheDocument()
    })

    it('should render BOI badges in both components', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const badges = screen.getAllByLabelText('Board of Ideators')
      expect(badges).toHaveLength(2)
    })
  })

  describe('State 1 Error Handling', () => {
    it('should pass error status to ExtractionAnimation when pipeline fails', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="FAILED"
          pipelineData={{
            ...mockPipelineData,
            stages: [
              {
                stageNumber: 1,
                status: 'failed',
                output: undefined,
                completedAt: undefined,
              },
            ],
          }}
        />
      )

      expect(screen.getByText(/Extraction encountered an error/i)).toBeInTheDocument()
    })

    it('should show error icon in ExtractionAnimation when status is FAILED', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="FAILED"
          pipelineData={{
            ...mockPipelineData,
            stages: [
              {
                stageNumber: 1,
                status: 'failed',
                output: undefined,
                completedAt: undefined,
              },
            ],
          }}
        />
      )

      const errorIcon = screen.getByLabelText('Error')
      expect(errorIcon).toBeInTheDocument()
    })
  })

  describe('State 1 Transitions', () => {
    it('should have transition classes on State 1 container', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const state1 = screen.getByTestId('state-1')
      expect(state1).toHaveClass('transition-all')
    })

    it('should have fade-in animation', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const state1 = screen.getByTestId('state-1')
      expect(state1).toHaveClass('ease-in-out')
    })
  })

  describe('State 1 Accessibility', () => {
    it('should have testid for testing', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      expect(screen.getByTestId('state-1')).toBeInTheDocument()
    })

    it('should have accessible labels on all interactive elements', () => {
      render(
        <PipelineStateMachine
          currentStage={1}
          status="PROCESSING"
          pipelineData={mockPipelineData}
        />
      )

      const badges = screen.getAllByLabelText('Board of Ideators')
      expect(badges.length).toBeGreaterThan(0)
    })
  })
})

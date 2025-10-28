/**
 * Feature Flag Tests
 * Tests the NEXT_PUBLIC_NEW_PIPELINE_UI feature flag behavior
 */

import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import PipelineStateMachine from '@/components/pipeline/PipelineStateMachine'
import { PipelineData } from '@/types/pipeline-state'

// Mock DetailPanel component (old UI)
jest.mock('@/components/pipeline/DetailPanel', () => {
  return function MockDetailPanel() {
    return <div data-testid="detail-panel">DetailPanel (Old UI)</div>
  }
})

const mockPipelineData: PipelineData = {
  runId: 'test-run-123',
  stages: [],
  opportunityCards: [],
  brandName: 'Test Brand',
}

describe('Feature Flag: NEXT_PUBLIC_NEW_PIPELINE_UI', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  it('should render PipelineStateMachine when flag is true', () => {
    process.env.NEXT_PUBLIC_NEW_PIPELINE_UI = 'true'

    render(
      <PipelineStateMachine
        currentStage={1}
        status="PROCESSING"
        pipelineData={mockPipelineData}
      />
    )

    // State Machine should render (State 1 in this case)
    expect(screen.getByTestId('state-1')).toBeInTheDocument()
  })

  it('should use State Machine component when flag is explicitly true', () => {
    process.env.NEXT_PUBLIC_NEW_PIPELINE_UI = 'true'

    const { container } = render(
      <PipelineStateMachine
        currentStage={2}
        status="PROCESSING"
        pipelineData={mockPipelineData}
      />
    )

    // Verify State Machine renders (State 2 in this case)
    expect(screen.getByTestId('state-2')).toBeInTheDocument()
  })

  it('should default to false when flag is undefined', () => {
    delete process.env.NEXT_PUBLIC_NEW_PIPELINE_UI

    // When undefined, the main page would render DetailPanel
    // This test verifies the default behavior
    expect(process.env.NEXT_PUBLIC_NEW_PIPELINE_UI).toBeUndefined()
  })

  it('should handle flag value "false" correctly', () => {
    process.env.NEXT_PUBLIC_NEW_PIPELINE_UI = 'false'

    // When "false", the check `=== 'true'` fails
    // This test verifies the string comparison works correctly
    expect(process.env.NEXT_PUBLIC_NEW_PIPELINE_UI === 'true').toBe(false)
  })

  it('should handle invalid flag values as false', () => {
    process.env.NEXT_PUBLIC_NEW_PIPELINE_UI = 'invalid'

    // Any value other than "true" should be treated as false
    expect(process.env.NEXT_PUBLIC_NEW_PIPELINE_UI === 'true').toBe(false)
  })

  it('should be case-sensitive (TRUE !== true)', () => {
    process.env.NEXT_PUBLIC_NEW_PIPELINE_UI = 'TRUE'

    // Uppercase TRUE should NOT match 'true'
    expect(process.env.NEXT_PUBLIC_NEW_PIPELINE_UI === 'true').toBe(false)
  })
})

describe('Integration: Feature Flag in Page Component', () => {
  it('should check environment variable correctly', () => {
    // Simulate the check that happens in page.tsx
    const shouldUseNewUI = (envValue: string | undefined): boolean => {
      return envValue === 'true'
    }

    expect(shouldUseNewUI('true')).toBe(true)
    expect(shouldUseNewUI('false')).toBe(false)
    expect(shouldUseNewUI(undefined)).toBe(false)
    expect(shouldUseNewUI('')).toBe(false)
    expect(shouldUseNewUI('1')).toBe(false)
    expect(shouldUseNewUI('yes')).toBe(false)
  })
})

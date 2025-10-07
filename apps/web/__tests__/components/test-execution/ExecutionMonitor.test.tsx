import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { ExecutionMonitor } from '@/components/test-execution/ExecutionMonitor';

describe('ExecutionMonitor', () => {
  const mockRunId = 'run-123';

  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Rendering', () => {
    it('should display run ID', () => {
      render(<ExecutionMonitor runId={mockRunId} />);
      expect(screen.getByText(mockRunId)).toBeInTheDocument();
    });

    it('should show all 5 stages', () => {
      render(<ExecutionMonitor runId={mockRunId} />);

      expect(screen.getByText(/Stage 1/)).toBeInTheDocument();
      expect(screen.getByText(/Stage 2/)).toBeInTheDocument();
      expect(screen.getByText(/Stage 3/)).toBeInTheDocument();
      expect(screen.getByText(/Stage 4/)).toBeInTheDocument();
      expect(screen.getByText(/Stage 5/)).toBeInTheDocument();
    });

    it('should display progress percentage', () => {
      render(<ExecutionMonitor runId={mockRunId} currentStage={3} />);
      expect(screen.getByText(/60%/)).toBeInTheDocument();
    });
  });

  describe('Status Updates', () => {
    it('should show pending status initially', () => {
      render(<ExecutionMonitor runId={mockRunId} status="pending" />);
      expect(screen.getByText(/pending/i)).toBeInTheDocument();
    });

    it('should update to running status', () => {
      const { rerender } = render(
        <ExecutionMonitor runId={mockRunId} status="pending" />
      );

      rerender(<ExecutionMonitor runId={mockRunId} status="running" currentStage={2} />);
      expect(screen.getByText(/running/i)).toBeInTheDocument();
    });

    it('should show completed status', () => {
      render(<ExecutionMonitor runId={mockRunId} status="completed" currentStage={5} />);
      expect(screen.getByText(/completed/i)).toBeInTheDocument();
    });

    it('should display error status and message', () => {
      render(
        <ExecutionMonitor
          runId={mockRunId}
          status="failed"
          errorMessage="Stage 3 failed: API timeout"
        />
      );

      expect(screen.getByText(/failed/i)).toBeInTheDocument();
      expect(screen.getByText(/API timeout/i)).toBeInTheDocument();
    });
  });

  describe('Progress Tracking', () => {
    it('should show progress bar', () => {
      render(<ExecutionMonitor runId={mockRunId} currentStage={3} />);

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '60');
    });

    it('should update progress as stages complete', () => {
      const { rerender } = render(
        <ExecutionMonitor runId={mockRunId} currentStage={1} />
      );

      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '20');

      rerender(<ExecutionMonitor runId={mockRunId} currentStage={4} />);
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '80');
    });

    it('should show 100% when completed', () => {
      render(<ExecutionMonitor runId={mockRunId} status="completed" currentStage={5} />);
      expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '100');
    });
  });

  describe('Cost Tracking', () => {
    it('should display estimated cost', () => {
      render(<ExecutionMonitor runId={mockRunId} estimatedCost={0.42} />);
      expect(screen.getByText(/\$0\.42/)).toBeInTheDocument();
    });

    it('should update actual cost as stages complete', () => {
      const { rerender } = render(
        <ExecutionMonitor runId={mockRunId} actualCost={0.15} />
      );

      expect(screen.getByText(/\$0\.15/)).toBeInTheDocument();

      rerender(<ExecutionMonitor runId={mockRunId} actualCost={0.32} />);
      expect(screen.getByText(/\$0\.32/)).toBeInTheDocument();
    });

    it('should show cost per stage', () => {
      const perStageCosts = {
        stage_1: 0.05,
        stage_2: 0.08,
        stage_3: 0.12,
        stage_4: 0.45,
        stage_5: 0.10,
      };

      render(<ExecutionMonitor runId={mockRunId} perStageCosts={perStageCosts} />);

      expect(screen.getByText(/\$0\.05/)).toBeInTheDocument();
      expect(screen.getByText(/\$0\.45/)).toBeInTheDocument();
    });
  });

  describe('Polling', () => {
    it('should poll for status updates', async () => {
      const mockFetch = vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'running', current_stage: 2 }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'completed', current_stage: 5 }),
        });

      global.fetch = mockFetch;

      render(<ExecutionMonitor runId={mockRunId} pollInterval={1000} />);

      await vi.advanceTimersByTimeAsync(1000);
      expect(mockFetch).toHaveBeenCalledTimes(1);

      await vi.advanceTimersByTimeAsync(1000);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('should stop polling when completed', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'completed', current_stage: 5 }),
      });

      global.fetch = mockFetch;

      render(<ExecutionMonitor runId={mockRunId} pollInterval={1000} />);

      await vi.advanceTimersByTimeAsync(5000);

      // Should stop polling after completion
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('Elapsed Time', () => {
    it('should display elapsed time', () => {
      render(<ExecutionMonitor runId={mockRunId} elapsedTime={125000} />);
      expect(screen.getByText(/2m 5s/)).toBeInTheDocument();
    });

    it('should update elapsed time automatically', async () => {
      vi.useRealTimers();
      render(<ExecutionMonitor runId={mockRunId} status="running" startTime={Date.now()} />);

      await waitFor(() => {
        expect(screen.getByText(/\d+s/)).toBeInTheDocument();
      }, { timeout: 2000 });
    });
  });

  describe('Stage Details', () => {
    it('should show model used for each stage', () => {
      const modelsUsed = {
        stage_1: 'deepseek-chat',
        stage_2: 'deepseek-chat',
        stage_3: 'deepseek-chat',
        stage_4: 'claude-sonnet-4',
        stage_5: 'deepseek-chat',
      };

      render(<ExecutionMonitor runId={mockRunId} modelsUsed={modelsUsed} />);

      expect(screen.getByText(/Claude Sonnet 4/)).toBeInTheDocument();
    });

    it('should highlight currently executing stage', () => {
      render(<ExecutionMonitor runId={mockRunId} currentStage={3} status="running" />);

      const stage3 = screen.getByTestId('stage-3');
      expect(stage3).toHaveClass('active');
    });

    it('should mark completed stages', () => {
      render(<ExecutionMonitor runId={mockRunId} currentStage={4} status="running" />);

      const stage1 = screen.getByTestId('stage-1');
      const stage2 = screen.getByTestId('stage-2');
      const stage3 = screen.getByTestId('stage-3');

      expect(stage1).toHaveClass('completed');
      expect(stage2).toHaveClass('completed');
      expect(stage3).toHaveClass('completed');
    });
  });

  describe('Actions', () => {
    it('should show cancel button for running execution', () => {
      render(<ExecutionMonitor runId={mockRunId} status="running" onCancel={vi.fn()} />);
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should call onCancel when cancel button clicked', async () => {
      const mockOnCancel = vi.fn();
      const user = userEvent.setup();

      render(<ExecutionMonitor runId={mockRunId} status="running" onCancel={mockOnCancel} />);

      await user.click(screen.getByRole('button', { name: /cancel/i }));
      expect(mockOnCancel).toHaveBeenCalledWith(mockRunId);
    });

    it('should show view results button when completed', () => {
      render(<ExecutionMonitor runId={mockRunId} status="completed" />);
      expect(screen.getByRole('button', { name: /view results/i })).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(<ExecutionMonitor runId={mockRunId} currentStage={3} />);

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-label', /pipeline progress/i);
    });

    it('should announce status changes', () => {
      const { rerender } = render(
        <ExecutionMonitor runId={mockRunId} status="pending" />
      );

      rerender(<ExecutionMonitor runId={mockRunId} status="running" currentStage={1} />);

      expect(screen.getByRole('status')).toHaveTextContent(/stage 1 running/i);
    });
  });
});

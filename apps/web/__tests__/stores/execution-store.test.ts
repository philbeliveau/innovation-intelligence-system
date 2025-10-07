import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useExecutionStore } from '@/stores/execution-store';

describe('ExecutionStore', () => {
  beforeEach(() => {
    const { result } = renderHook(() => useExecutionStore());
    act(() => {
      result.current.reset();
    });
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with empty state', () => {
      const { result } = renderHook(() => useExecutionStore());

      expect(result.current.currentRun).toBeNull();
      expect(result.current.isPolling).toBe(false);
      expect(result.current.runHistory).toEqual([]);
    });
  });

  describe('Starting Execution', () => {
    it('should start execution with run details', () => {
      const { result } = renderHook(() => useExecutionStore());

      const runDetails = {
        runId: 'run-123',
        inputId: 'input-1',
        brandId: 'brand-1',
        estimatedCost: 0.42,
      };

      act(() => {
        result.current.startExecution(runDetails);
      });

      expect(result.current.currentRun).toMatchObject({
        runId: 'run-123',
        status: 'pending',
        estimatedCost: 0.42,
      });
    });

    it('should start polling when execution begins', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({
          runId: 'run-123',
          inputId: 'input-1',
          brandId: 'brand-1',
        });
      });

      expect(result.current.isPolling).toBe(true);
    });
  });

  describe('Status Updates', () => {
    it('should update status from polling', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({
          status: 'running',
          current_stage: 2,
          actual_cost_usd: 0.15,
        });
      });

      expect(result.current.currentRun?.status).toBe('running');
      expect(result.current.currentRun?.currentStage).toBe(2);
      expect(result.current.currentRun?.actualCost).toBe(0.15);
    });

    it('should stop polling when execution completes', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({
          status: 'completed',
          current_stage: 5,
        });
      });

      expect(result.current.isPolling).toBe(false);
    });

    it('should stop polling when execution fails', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({
          status: 'failed',
          error_message: 'Stage 3 timeout',
        });
      });

      expect(result.current.isPolling).toBe(false);
      expect(result.current.currentRun?.errorMessage).toBe('Stage 3 timeout');
    });
  });

  describe('Progress Calculation', () => {
    it('should calculate progress percentage', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({ current_stage: 3, status: 'running' });
      });

      expect(result.current.getProgressPercentage()).toBe(60);
    });

    it('should return 0% for pending status', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
      });

      expect(result.current.getProgressPercentage()).toBe(0);
    });

    it('should return 100% for completed status', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });
      });

      expect(result.current.getProgressPercentage()).toBe(100);
    });
  });

  describe('Run History', () => {
    it('should add completed run to history', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });
      });

      expect(result.current.runHistory).toHaveLength(1);
      expect(result.current.runHistory[0].runId).toBe('run-123');
    });

    it('should maintain history of multiple runs', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-1' } as any);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });

        result.current.startExecution({ runId: 'run-2' } as any);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });
      });

      expect(result.current.runHistory).toHaveLength(2);
    });

    it('should limit history size', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        for (let i = 1; i <= 25; i++) {
          result.current.startExecution({ runId: `run-${i}` } as any);
          result.current.updateStatus({ status: 'completed', current_stage: 5 });
        }
      });

      expect(result.current.runHistory.length).toBeLessThanOrEqual(20);
    });

    it('should retrieve run from history', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });
      });

      const historicalRun = result.current.getRunFromHistory('run-123');
      expect(historicalRun?.runId).toBe('run-123');
    });
  });

  describe('Polling Control', () => {
    it('should manually stop polling', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.stopPolling();
      });

      expect(result.current.isPolling).toBe(false);
    });

    it('should manually start polling', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.stopPolling();
        result.current.startPolling();
      });

      expect(result.current.isPolling).toBe(true);
    });

    it('should configure polling interval', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.setPollingInterval(5000);
      });

      expect(result.current.pollingInterval).toBe(5000);
    });
  });

  describe('Cancellation', () => {
    it('should cancel execution', async () => {
      const mockCancelFn = vi.fn().mockResolvedValue({ success: true });
      global.fetch = mockCancelFn;

      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
      });

      await act(async () => {
        await result.current.cancelExecution();
      });

      expect(mockCancelFn).toHaveBeenCalled();
      expect(result.current.currentRun?.status).toBe('cancelled');
    });
  });

  describe('Error Handling', () => {
    it('should handle polling errors gracefully', async () => {
      const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));
      global.fetch = mockFetch;

      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
      });

      await waitFor(() => {
        expect(result.current.pollingError).toBeTruthy();
      });
    });

    it('should retry polling after error', async () => {
      const mockFetch = vi
        .fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'running', current_stage: 2 }),
        });

      global.fetch = mockFetch;

      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
      });

      await waitFor(() => {
        expect(result.current.currentRun?.currentStage).toBe(2);
      });

      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Elapsed Time', () => {
    it('should track elapsed time', () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
      });

      act(() => {
        vi.advanceTimersByTime(30000); // 30 seconds
      });

      expect(result.current.getElapsedTime()).toBeGreaterThanOrEqual(30000);

      vi.useRealTimers();
    });

    it('should stop tracking time when completed', () => {
      vi.useFakeTimers();

      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        vi.advanceTimersByTime(10000);
        result.current.updateStatus({ status: 'completed', current_stage: 5 });
      });

      const completedTime = result.current.getElapsedTime();

      act(() => {
        vi.advanceTimersByTime(10000);
      });

      expect(result.current.getElapsedTime()).toBe(completedTime);

      vi.useRealTimers();
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStatus({ status: 'running', current_stage: 3 });
        result.current.reset();
      });

      expect(result.current.currentRun).toBeNull();
      expect(result.current.isPolling).toBe(false);
    });

    it('should stop polling on reset', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.reset();
      });

      expect(result.current.isPolling).toBe(false);
    });
  });

  describe('Per-Stage Costs', () => {
    it('should track costs per stage', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStageCost(1, 0.05);
        result.current.updateStageCost(2, 0.08);
      });

      expect(result.current.currentRun?.perStageCosts).toEqual({
        stage_1: 0.05,
        stage_2: 0.08,
        stage_3: 0,
        stage_4: 0,
        stage_5: 0,
      });
    });

    it('should calculate total actual cost from stage costs', () => {
      const { result } = renderHook(() => useExecutionStore());

      act(() => {
        result.current.startExecution({ runId: 'run-123' } as any);
        result.current.updateStageCost(1, 0.05);
        result.current.updateStageCost(2, 0.08);
        result.current.updateStageCost(3, 0.12);
      });

      expect(result.current.getTotalActualCost()).toBeCloseTo(0.25, 2);
    });
  });
});

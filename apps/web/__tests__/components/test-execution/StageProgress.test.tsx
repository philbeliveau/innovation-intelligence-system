import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { StageProgress } from '@/components/test-execution/StageProgress';

describe('StageProgress', () => {
  describe('Status Indicators', () => {
    it('should show pending status', () => {
      render(<StageProgress stage={1} status="pending" />);
      expect(screen.getByTestId('stage-1-status')).toHaveTextContent(/pending/i);
    });

    it('should show running status with spinner', () => {
      render(<StageProgress stage={2} status="running" />);

      expect(screen.getByTestId('stage-2-status')).toHaveTextContent(/running/i);
      expect(screen.getByTestId('spinner')).toBeInTheDocument();
    });

    it('should show completed status with checkmark', () => {
      render(<StageProgress stage={3} status="completed" />);

      expect(screen.getByTestId('stage-3-status')).toHaveTextContent(/completed/i);
      expect(screen.getByTestId('checkmark-icon')).toBeInTheDocument();
    });

    it('should show failed status with error icon', () => {
      render(<StageProgress stage={4} status="failed" errorMessage="API timeout" />);

      expect(screen.getByTestId('stage-4-status')).toHaveTextContent(/failed/i);
      expect(screen.getByTestId('error-icon')).toBeInTheDocument();
      expect(screen.getByText(/API timeout/i)).toBeInTheDocument();
    });
  });

  describe('Stage Information', () => {
    it('should display stage number and name', () => {
      render(<StageProgress stage={1} stageName="Input Processing" />);

      expect(screen.getByText(/Stage 1/)).toBeInTheDocument();
      expect(screen.getByText(/Input Processing/)).toBeInTheDocument();
    });

    it('should show model being used', () => {
      render(<StageProgress stage={4} modelId="claude-sonnet-4" />);
      expect(screen.getByText(/Claude Sonnet 4/i)).toBeInTheDocument();
    });

    it('should display duration when completed', () => {
      render(<StageProgress stage={2} status="completed" duration={45000} />);
      expect(screen.getByText(/45s/)).toBeInTheDocument();
    });

    it('should show token usage', () => {
      render(
        <StageProgress
          stage={3}
          status="completed"
          tokensUsed={{ input: 1500, output: 800 }}
        />
      );

      expect(screen.getByText(/1,500 in/)).toBeInTheDocument();
      expect(screen.getByText(/800 out/)).toBeInTheDocument();
    });
  });

  describe('Cost Display', () => {
    it('should show stage cost', () => {
      render(<StageProgress stage={4} status="completed" cost={0.45} />);
      expect(screen.getByText(/\$0\.45/)).toBeInTheDocument();
    });

    it('should highlight expensive stages', () => {
      render(<StageProgress stage={4} cost={2.50} highlightExpensive />);

      const costElement = screen.getByTestId('stage-cost');
      expect(costElement).toHaveClass('cost-high');
    });
  });

  describe('Progress Animation', () => {
    it('should show progress bar for running stage', () => {
      render(<StageProgress stage={2} status="running" progress={65} />);

      const progressBar = screen.getByRole('progressbar');
      expect(progressBar).toHaveAttribute('aria-valuenow', '65');
    });

    it('should show indeterminate progress when percentage unknown', () => {
      render(<StageProgress stage={3} status="running" />);

      expect(screen.getByTestId('indeterminate-progress')).toBeInTheDocument();
    });
  });

  describe('Visual States', () => {
    it('should use muted styling for pending stages', () => {
      render(<StageProgress stage={5} status="pending" />);

      const stageCard = screen.getByTestId('stage-5-card');
      expect(stageCard).toHaveClass('opacity-50');
    });

    it('should highlight active running stage', () => {
      render(<StageProgress stage={2} status="running" />);

      const stageCard = screen.getByTestId('stage-2-card');
      expect(stageCard).toHaveClass('border-primary');
    });

    it('should show success styling for completed stages', () => {
      render(<StageProgress stage={1} status="completed" />);

      const stageCard = screen.getByTestId('stage-1-card');
      expect(stageCard).toHaveClass('border-success');
    });

    it('should show error styling for failed stages', () => {
      render(<StageProgress stage={3} status="failed" />);

      const stageCard = screen.getByTestId('stage-3-card');
      expect(stageCard).toHaveClass('border-destructive');
    });
  });

  describe('Expandable Details', () => {
    it('should expand to show additional details', async () => {
      const user = userEvent.setup();
      render(
        <StageProgress
          stage={4}
          status="completed"
          tokensUsed={{ input: 15000, output: 5000 }}
          expandable
        />
      );

      const expandButton = screen.getByRole('button', { name: /show details/i });
      await user.click(expandButton);

      expect(screen.getByText(/Token Breakdown/i)).toBeInTheDocument();
      expect(screen.getByText(/15,000/)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<StageProgress stage={3} status="running" />);

      expect(screen.getByRole('region')).toHaveAttribute(
        'aria-label',
        /Stage 3/i
      );
    });

    it('should announce status changes', () => {
      const { rerender } = render(<StageProgress stage={2} status="pending" />);

      rerender(<StageProgress stage={2} status="running" />);

      expect(screen.getByRole('status')).toHaveTextContent(/Stage 2 is now running/i);
    });
  });
});

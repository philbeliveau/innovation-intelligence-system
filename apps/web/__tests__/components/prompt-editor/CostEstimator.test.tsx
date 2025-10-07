import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CostEstimator } from '@/components/prompt-editor/CostEstimator';
import type { PromptConfiguration } from '@/types';

describe('CostEstimator', () => {
  const mockConfig: PromptConfiguration = {
    id: 'test-config',
    name: 'Test Config',
    description: null,
    stage_1_prompt: 'Test prompt',
    stage_2_prompt: 'Test prompt',
    stage_3_prompt: 'Test prompt',
    stage_4_prompt: 'Test prompt',
    stage_5_prompt: 'Test prompt',
    default_model_id: 'deepseek-chat',
    stage_model_overrides: {},
    created_at: new Date(),
    updated_at: new Date(),
    is_default: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should display total estimated cost', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      expect(screen.getByText(/estimated cost/i)).toBeInTheDocument();
      expect(screen.getByText(/\$\d+\.\d{2}/)).toBeInTheDocument();
    });

    it('should show cost for each stage', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      expect(screen.getByText(/stage 1/i)).toBeInTheDocument();
      expect(screen.getByText(/stage 2/i)).toBeInTheDocument();
      expect(screen.getByText(/stage 3/i)).toBeInTheDocument();
      expect(screen.getByText(/stage 4/i)).toBeInTheDocument();
      expect(screen.getByText(/stage 5/i)).toBeInTheDocument();
    });

    it('should display model used for each stage', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      const stageCosts = screen.getAllByTestId(/stage-\d-cost/);
      stageCosts.forEach(stageCost => {
        expect(within(stageCost).getByText(/deepseek/i)).toBeInTheDocument();
      });
    });

    it('should show breakdown when expanded', async () => {
      const user = userEvent.setup();
      render(<CostEstimator config={mockConfig} numRuns={1} expandable />);

      const expandButton = screen.getByRole('button', { name: /show breakdown/i });
      await user.click(expandButton);

      expect(screen.getByText(/input tokens/i)).toBeInTheDocument();
      expect(screen.getByText(/output tokens/i)).toBeInTheDocument();
    });
  });

  describe('Cost Calculations', () => {
    it('should calculate cost for single run', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      const totalCost = screen.getByTestId('total-cost');
      expect(totalCost.textContent).toMatch(/\$0\.\d{2}/);
    });

    it('should calculate cost for multiple runs', () => {
      const { rerender } = render(<CostEstimator config={mockConfig} numRuns={1} />);
      const singleRunCost = screen.getByTestId('total-cost').textContent;

      rerender(<CostEstimator config={mockConfig} numRuns={10} />);
      const multipleRunsCost = screen.getByTestId('total-cost').textContent;

      // Cost should be 10x for 10 runs
      const singleValue = parseFloat(singleRunCost!.replace('$', ''));
      const multipleValue = parseFloat(multipleRunsCost!.replace('$', ''));

      expect(multipleValue).toBeCloseTo(singleValue * 10, 2);
    });

    it('should apply model overrides to cost calculation', () => {
      const configWithOverride = {
        ...mockConfig,
        stage_model_overrides: {
          stage_4: 'claude-sonnet-4',
        },
      };

      const { rerender } = render(<CostEstimator config={mockConfig} numRuns={1} />);
      const baseCost = parseFloat(
        screen.getByTestId('total-cost').textContent!.replace('$', '')
      );

      rerender(<CostEstimator config={configWithOverride} numRuns={1} />);
      const overrideCost = parseFloat(
        screen.getByTestId('total-cost').textContent!.replace('$', '')
      );

      // Cost should be higher with Claude Sonnet 4 override
      expect(overrideCost).toBeGreaterThan(baseCost);
    });

    it('should show per-stage cost breakdown', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} showBreakdown />);

      const stage1Cost = screen.getByTestId('stage-1-cost');
      const stage2Cost = screen.getByTestId('stage-2-cost');
      const stage4Cost = screen.getByTestId('stage-4-cost');

      expect(stage1Cost.textContent).toMatch(/\$\d+\.\d{2}/);
      expect(stage2Cost.textContent).toMatch(/\$\d+\.\d{2}/);
      expect(stage4Cost.textContent).toMatch(/\$\d+\.\d{2}/);
    });
  });

  describe('Budget Warnings', () => {
    it('should show warning when approaching budget limit', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={100}
          budgetLimit={1.00}
        />
      );

      expect(screen.getByText(/approaching budget/i)).toBeInTheDocument();
    });

    it('should show error when exceeding budget limit', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={1000}
          budgetLimit={1.00}
        />
      );

      expect(screen.getByText(/exceeds budget/i)).toBeInTheDocument();
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });

    it('should not show warning when within budget', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={1}
          budgetLimit={10.00}
        />
      );

      expect(screen.queryByText(/budget/i)).not.toBeInTheDocument();
    });

    it('should show percentage of budget used', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={10}
          budgetLimit={10.00}
          showBudgetPercentage
        />
      );

      expect(screen.getByText(/\d+% of budget/i)).toBeInTheDocument();
    });
  });

  describe('Model Override Visualization', () => {
    it('should highlight stages with model overrides', () => {
      const configWithOverride = {
        ...mockConfig,
        stage_model_overrides: {
          stage_4: 'claude-sonnet-4',
        },
      };

      render(<CostEstimator config={configWithOverride} numRuns={1} />);

      const stage4 = screen.getByTestId('stage-4-cost');
      expect(stage4).toHaveClass('model-override');
      expect(within(stage4).getByText(/Claude Sonnet 4/i)).toBeInTheDocument();
    });

    it('should show cost increase from override', () => {
      const configWithOverride = {
        ...mockConfig,
        stage_model_overrides: {
          stage_4: 'claude-sonnet-4',
        },
      };

      render(
        <CostEstimator
          config={configWithOverride}
          numRuns={1}
          showCostIncrease
        />
      );

      const stage4 = screen.getByTestId('stage-4-cost');
      expect(within(stage4).getByText(/\+\d+%/)).toBeInTheDocument();
    });
  });

  describe('Token Estimates', () => {
    it('should display estimated input and output tokens', () => {
      render(
        <CostEstimator config={mockConfig} numRuns={1} showTokens />
      );

      expect(screen.getByText(/input tokens/i)).toBeInTheDocument();
      expect(screen.getByText(/output tokens/i)).toBeInTheDocument();
    });

    it('should show total token count', () => {
      render(
        <CostEstimator config={mockConfig} numRuns={1} showTotalTokens />
      );

      expect(screen.getByText(/total tokens/i)).toBeInTheDocument();
      expect(screen.getByText(/\d+ tokens/)).toBeInTheDocument();
    });

    it('should account for research data in Stage 4 token estimate', () => {
      render(
        <CostEstimator config={mockConfig} numRuns={1} showBreakdown />
      );

      const stage4Tokens = screen.getByTestId('stage-4-tokens');
      const stage1Tokens = screen.getByTestId('stage-1-tokens');

      // Stage 4 should have significantly more tokens due to research injection
      const stage4Count = parseInt(stage4Tokens.textContent!.replace(/\D/g, ''));
      const stage1Count = parseInt(stage1Tokens.textContent!.replace(/\D/g, ''));

      expect(stage4Count).toBeGreaterThan(stage1Count * 2);
    });
  });

  describe('Comparison Mode', () => {
    it('should compare costs between different configurations', () => {
      const cheapConfig = mockConfig;
      const expensiveConfig = {
        ...mockConfig,
        default_model_id: 'claude-sonnet-4',
      };

      render(
        <CostEstimator
          config={cheapConfig}
          numRuns={1}
          compareWith={expensiveConfig}
        />
      );

      expect(screen.getByText(/\d+% cheaper/i)).toBeInTheDocument();
    });

    it('should show cost savings amount', () => {
      const cheapConfig = mockConfig;
      const expensiveConfig = {
        ...mockConfig,
        default_model_id: 'claude-sonnet-4',
      };

      render(
        <CostEstimator
          config={cheapConfig}
          numRuns={1}
          compareWith={expensiveConfig}
          showSavings
        />
      );

      expect(screen.getByText(/saves \$\d+\.\d{2}/i)).toBeInTheDocument();
    });
  });

  describe('Interactive Features', () => {
    it('should allow changing number of runs', async () => {
      const user = userEvent.setup();
      const mockOnRunsChange = vi.fn();

      render(
        <CostEstimator
          config={mockConfig}
          numRuns={1}
          onRunsChange={mockOnRunsChange}
          interactive
        />
      );

      const runsInput = screen.getByLabelText(/number of runs/i);
      await user.clear(runsInput);
      await user.type(runsInput, '10');

      expect(mockOnRunsChange).toHaveBeenCalledWith(10);
    });

    it('should update cost in real-time when runs change', async () => {
      const user = userEvent.setup();
      const { rerender } = render(
        <CostEstimator config={mockConfig} numRuns={1} />
      );

      const initialCost = screen.getByTestId('total-cost').textContent;

      rerender(<CostEstimator config={mockConfig} numRuns={5} />);

      const updatedCost = screen.getByTestId('total-cost').textContent;
      expect(updatedCost).not.toBe(initialCost);
    });

    it('should allow toggling between simplified and detailed view', async () => {
      const user = userEvent.setup();
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      const toggleButton = screen.getByRole('button', { name: /show details/i });
      await user.click(toggleButton);

      expect(screen.getByText(/token breakdown/i)).toBeInTheDocument();
    });
  });

  describe('Formatting', () => {
    it('should format costs to 2 decimal places', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      const costs = screen.getAllByText(/\$\d+\.\d{2}/);
      expect(costs.length).toBeGreaterThan(0);
    });

    it('should use currency symbol based on locale', () => {
      render(
        <CostEstimator config={mockConfig} numRuns={1} currency="EUR" />
      );

      expect(screen.getByText(/€/)).toBeInTheDocument();
    });

    it('should abbreviate large token counts', () => {
      render(
        <CostEstimator config={mockConfig} numRuns={100} showTokens />
      );

      expect(screen.getByText(/\d+k tokens/i)).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading skeleton while calculating', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} loading />);

      expect(screen.getByTestId('cost-skeleton')).toBeInTheDocument();
    });

    it('should show actual costs after loading completes', () => {
      const { rerender } = render(
        <CostEstimator config={mockConfig} numRuns={1} loading />
      );

      rerender(<CostEstimator config={mockConfig} numRuns={1} loading={false} />);

      expect(screen.queryByTestId('cost-skeleton')).not.toBeInTheDocument();
      expect(screen.getByText(/\$\d+\.\d{2}/)).toBeInTheDocument();
    });
  });

  describe('Visual Indicators', () => {
    it('should use color coding for cost levels', () => {
      const expensiveConfig = {
        ...mockConfig,
        default_model_id: 'claude-sonnet-4',
      };

      render(<CostEstimator config={expensiveConfig} numRuns={100} />);

      const totalCost = screen.getByTestId('total-cost');
      expect(totalCost).toHaveClass('cost-high');
    });

    it('should show progress bar for budget usage', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={50}
          budgetLimit={10.00}
          showProgress
        />
      );

      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should highlight most expensive stage', () => {
      const configWithOverride = {
        ...mockConfig,
        stage_model_overrides: {
          stage_4: 'claude-sonnet-4',
        },
      };

      render(
        <CostEstimator
          config={configWithOverride}
          numRuns={1}
          highlightExpensive
        />
      );

      const stage4 = screen.getByTestId('stage-4-cost');
      expect(stage4).toHaveClass('most-expensive');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<CostEstimator config={mockConfig} numRuns={1} />);

      expect(screen.getByLabelText(/estimated cost/i)).toBeInTheDocument();
    });

    it('should announce cost updates to screen readers', async () => {
      const { rerender } = render(
        <CostEstimator config={mockConfig} numRuns={1} />
      );

      rerender(<CostEstimator config={mockConfig} numRuns={10} />);

      expect(screen.getByRole('status')).toHaveTextContent(/cost updated/i);
    });

    it('should have proper color contrast for warnings', () => {
      render(
        <CostEstimator
          config={mockConfig}
          numRuns={1000}
          budgetLimit={1.00}
        />
      );

      const warning = screen.getByRole('alert');
      // Should have sufficient contrast ratio
      expect(warning).toHaveStyle({ color: expect.stringMatching(/#[0-9a-f]{6}/i) });
    });
  });

  describe('Error Handling', () => {
    it('should handle invalid configuration gracefully', () => {
      const invalidConfig = {
        ...mockConfig,
        default_model_id: 'invalid-model',
      };

      render(<CostEstimator config={invalidConfig} numRuns={1} />);

      expect(screen.getByText(/unable to estimate/i)).toBeInTheDocument();
    });

    it('should handle zero runs', () => {
      render(<CostEstimator config={mockConfig} numRuns={0} />);

      expect(screen.getByText(/\$0\.00/)).toBeInTheDocument();
    });

    it('should handle negative runs input', () => {
      render(<CostEstimator config={mockConfig} numRuns={-1} />);

      expect(screen.getByText(/invalid/i)).toBeInTheDocument();
    });
  });
});

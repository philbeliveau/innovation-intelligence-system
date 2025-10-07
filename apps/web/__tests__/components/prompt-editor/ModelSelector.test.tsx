import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ModelSelector } from '@/components/prompt-editor/ModelSelector';
import { AVAILABLE_MODELS } from '@/lib/models';

describe('ModelSelector', () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render with default model', () => {
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      expect(screen.getByRole('combobox')).toBeInTheDocument();
      expect(screen.getByText(/deepseek/i)).toBeInTheDocument();
    });

    it('should display selected model name', () => {
      render(
        <ModelSelector value="claude-sonnet-4" onChange={mockOnChange} />
      );

      expect(screen.getByText(/Claude Sonnet 4/i)).toBeInTheDocument();
    });

    it('should show model pricing information', () => {
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} showPricing />
      );

      expect(screen.getByText(/\$0\.14/)).toBeInTheDocument();
    });
  });

  describe('Model Selection', () => {
    it('should open dropdown on click', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      const selector = screen.getByRole('combobox');
      await user.click(selector);

      expect(screen.getByRole('listbox')).toBeInTheDocument();
    });

    it('should display all available models in dropdown', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));

      const listbox = screen.getByRole('listbox');
      const options = within(listbox).getAllByRole('option');

      expect(options.length).toBe(AVAILABLE_MODELS.length);
    });

    it('should call onChange when model is selected', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      await user.click(screen.getByText(/Claude Sonnet 4/i));

      expect(mockOnChange).toHaveBeenCalledWith('claude-sonnet-4');
    });

    it('should close dropdown after selection', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      await user.click(screen.getByText(/GPT-4o Mini/i));

      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });

    it('should not call onChange when selecting current model', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      await user.click(screen.getByText(/DeepSeek Chat/i));

      expect(mockOnChange).not.toHaveBeenCalled();
    });
  });

  describe('Model Information Display', () => {
    it('should show model provider', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} showProvider />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/deepseek/i)).toBeInTheDocument();
    });

    it('should show context window size', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="claude-sonnet-4" onChange={mockOnChange} showContext />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/200k/i)).toBeInTheDocument();
    });

    it('should show model capabilities', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="claude-sonnet-4" onChange={mockOnChange} showCapabilities />
      );

      await user.click(screen.getByRole('combobox'));

      const option = screen.getByText(/Claude Sonnet 4/i).closest('[role="option"]');
      expect(option).toBeInTheDocument();
      expect(within(option!).getByText(/vision/i)).toBeInTheDocument();
    });

    it('should show recommended use case', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/cost-effective/i)).toBeInTheDocument();
    });
  });

  describe('Pricing Display', () => {
    it('should show input and output pricing separately', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} showDetailedPricing />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/input.*\$0\.14/i)).toBeInTheDocument();
      expect(screen.getByText(/output.*\$0\.28/i)).toBeInTheDocument();
    });

    it('should highlight cheapest model', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} highlightCheapest />
      );

      await user.click(screen.getByRole('combobox'));

      const cheapestOption = screen.getByText(/DeepSeek Chat/i).closest('[role="option"]');
      expect(cheapestOption).toHaveClass('cheapest-model');
    });

    it('should show cost comparison badge', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector
          value="deepseek-chat"
          onChange={mockOnChange}
          showCostComparison
          comparisonBase="claude-sonnet-4"
        />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/95% cheaper/i)).toBeInTheDocument();
    });
  });

  describe('Filtering and Search', () => {
    it('should filter models by provider', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector
          value="deepseek-chat"
          onChange={mockOnChange}
          filterProvider="anthropic"
        />
      );

      await user.click(screen.getByRole('combobox'));

      const options = screen.getAllByRole('option');
      expect(options.length).toBe(2); // Claude Haiku and Sonnet
    });

    it('should filter models by capability', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector
          value="claude-sonnet-4"
          onChange={mockOnChange}
          filterCapability="vision"
        />
      );

      await user.click(screen.getByRole('combobox'));

      const options = screen.getAllByRole('option');
      options.forEach(option => {
        const modelName = option.textContent;
        // Vision models should be Claude Sonnet 4, GPT-4o, GPT-4o Mini
        expect(['Claude Sonnet 4', 'GPT-4o', 'GPT-4o Mini'].some(name =>
          modelName?.includes(name)
        )).toBe(true);
      });
    });

    it('should support search/filter by text', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} searchable />
      );

      const searchInput = screen.getByPlaceholderText(/search models/i);
      await user.type(searchInput, 'claude');

      const options = screen.getAllByRole('option');
      options.forEach(option => {
        expect(option.textContent?.toLowerCase()).toContain('claude');
      });
    });
  });

  describe('Grouping', () => {
    it('should group models by provider', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} groupByProvider />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/Anthropic/i)).toBeInTheDocument();
      expect(screen.getByText(/OpenAI/i)).toBeInTheDocument();
      expect(screen.getByText(/DeepSeek/i)).toBeInTheDocument();
    });

    it('should group models by price tier', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} groupByPrice />
      );

      await user.click(screen.getByRole('combobox'));

      expect(screen.getByText(/Budget/i)).toBeInTheDocument();
      expect(screen.getByText(/Premium/i)).toBeInTheDocument();
    });
  });

  describe('Validation', () => {
    it('should handle invalid model ID gracefully', () => {
      render(
        <ModelSelector value="invalid-model" onChange={mockOnChange} />
      );

      expect(screen.getByText(/Select a model/i)).toBeInTheDocument();
    });

    it('should show error state when required but no model selected', () => {
      render(
        <ModelSelector value="" onChange={mockOnChange} required />
      );

      expect(screen.getByRole('combobox')).toHaveAttribute('aria-invalid', 'true');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should navigate options with arrow keys', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      const selector = screen.getByRole('combobox');
      selector.focus();

      await user.keyboard('{ArrowDown}');
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Enter}');

      expect(mockOnChange).toHaveBeenCalled();
    });

    it('should select with Enter key', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      await user.keyboard('{ArrowDown}');
      await user.keyboard('{Enter}');

      expect(mockOnChange).toHaveBeenCalled();
    });

    it('should close with Escape key', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      expect(screen.getByRole('listbox')).toBeInTheDocument();

      await user.keyboard('{Escape}');
      expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
    });
  });

  describe('Visual Indicators', () => {
    it('should show recommended badge for suggested models', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector
          value="deepseek-chat"
          onChange={mockOnChange}
          recommendedStage={1}
        />
      );

      await user.click(screen.getByRole('combobox'));

      // DeepSeek should be recommended for cost-effective stages
      const option = screen.getByText(/DeepSeek Chat/i).closest('[role="option"]');
      expect(within(option!).getByText(/recommended/i)).toBeInTheDocument();
    });

    it('should show warning for expensive models', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} showWarnings />
      );

      await user.click(screen.getByRole('combobox'));

      const expensiveOption = screen.getByText(/Claude Sonnet 4/i).closest('[role="option"]');
      expect(within(expensiveOption!).getByTestId('expensive-warning')).toBeInTheDocument();
    });

    it('should show loading state while fetching models', () => {
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} loading />
      );

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      const selector = screen.getByRole('combobox');
      expect(selector).toHaveAttribute('aria-haspopup', 'listbox');
      expect(selector).toHaveAttribute('aria-expanded', 'false');
    });

    it('should announce selected model to screen readers', async () => {
      const user = userEvent.setup();
      render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      await user.click(screen.getByRole('combobox'));
      await user.click(screen.getByText(/Claude Sonnet 4/i));

      expect(screen.getByRole('combobox')).toHaveAccessibleName(/Claude Sonnet 4/i);
    });
  });

  describe('Performance', () => {
    it('should not re-render unnecessarily', () => {
      const { rerender } = render(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      const renderCount = vi.fn();
      vi.spyOn(React, 'useMemo').mockImplementation(renderCount);

      rerender(
        <ModelSelector value="deepseek-chat" onChange={mockOnChange} />
      );

      // Should use memoization to prevent unnecessary re-renders
      expect(renderCount).not.toHaveBeenCalled();
    });
  });
});

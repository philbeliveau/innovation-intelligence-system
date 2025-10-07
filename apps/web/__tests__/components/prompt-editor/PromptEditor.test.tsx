import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PromptEditor } from '@/components/prompt-editor/PromptEditor';
import type { PromptConfiguration } from '@/types';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  default: ({ value, onChange }: any) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
    />
  ),
}));

describe('PromptEditor', () => {
  const mockOnSave = vi.fn();
  const mockConfig: PromptConfiguration = {
    id: 'test-config-123',
    name: 'Test Configuration',
    description: 'Test description',
    stage_1_prompt: 'Stage 1 prompt',
    stage_2_prompt: 'Stage 2 prompt',
    stage_3_prompt: 'Stage 3 prompt',
    stage_4_prompt: 'Stage 4 prompt',
    stage_5_prompt: 'Stage 5 prompt',
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
    it('should render with initial configuration', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByText('Test Configuration')).toBeInTheDocument();
      expect(screen.getByText(/Stage 1/)).toBeInTheDocument();
    });

    it('should render all 5 stage tabs', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByRole('tab', { name: /Stage 1/ })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Stage 2/ })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Stage 3/ })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Stage 4/ })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /Stage 5/ })).toBeInTheDocument();
    });

    it('should render without initial configuration', () => {
      render(<PromptEditor onSave={mockOnSave} />);

      expect(screen.getByRole('tab', { name: /Stage 1/ })).toBeInTheDocument();
    });

    it('should render save button', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByRole('button', { name: /Save/i })).toBeInTheDocument();
    });
  });

  describe('Stage Navigation', () => {
    it('should switch between stages', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      // Click Stage 2 tab
      await user.click(screen.getByRole('tab', { name: /Stage 2/ }));

      // Editor should show Stage 2 prompt
      const editor = screen.getByTestId('monaco-editor');
      expect(editor).toHaveValue('Stage 2 prompt');
    });

    it('should preserve prompt content when switching stages', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      // Edit Stage 1
      const editor = screen.getByTestId('monaco-editor');
      await user.clear(editor);
      await user.type(editor, 'Modified Stage 1');

      // Switch to Stage 2
      await user.click(screen.getByRole('tab', { name: /Stage 2/ }));

      // Switch back to Stage 1
      await user.click(screen.getByRole('tab', { name: /Stage 1/ }));

      // Should still have modified content
      expect(editor).toHaveValue('Modified Stage 1');
    });

    it('should show active stage indicator', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const stage3Tab = screen.getByRole('tab', { name: /Stage 3/ });
      await user.click(stage3Tab);

      expect(stage3Tab).toHaveAttribute('data-state', 'active');
    });
  });

  describe('Prompt Editing', () => {
    it('should update prompt content', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const editor = screen.getByTestId('monaco-editor');
      await user.clear(editor);
      await user.type(editor, 'New prompt content');

      expect(editor).toHaveValue('New prompt content');
    });

    it('should handle multi-line prompts', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const editor = screen.getByTestId('monaco-editor');
      const multiLinePrompt = 'Line 1\nLine 2\nLine 3';

      await user.clear(editor);
      await user.type(editor, multiLinePrompt);

      expect(editor.value).toContain('Line 1');
      expect(editor.value).toContain('Line 2');
      expect(editor.value).toContain('Line 3');
    });

    it('should update all stages independently', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      // Edit Stage 1
      const editor = screen.getByTestId('monaco-editor');
      await user.clear(editor);
      await user.type(editor, 'Modified Stage 1');

      // Switch to Stage 2 and edit
      await user.click(screen.getByRole('tab', { name: /Stage 2/ }));
      await user.clear(editor);
      await user.type(editor, 'Modified Stage 2');

      // Verify both changes persist
      await user.click(screen.getByRole('tab', { name: /Stage 1/ }));
      expect(editor).toHaveValue('Modified Stage 1');

      await user.click(screen.getByRole('tab', { name: /Stage 2/ }));
      expect(editor).toHaveValue('Modified Stage 2');
    });
  });

  describe('Model Selection', () => {
    it('should show default model selector', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByText(/deepseek/i)).toBeInTheDocument();
    });

    it('should allow model override per stage', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      // Switch to Stage 4
      await user.click(screen.getByRole('tab', { name: /Stage 4/ }));

      // Select different model (assuming ModelSelector component is rendered)
      const modelSelector = screen.getByRole('combobox');
      await user.click(modelSelector);

      const claudeOption = screen.getByText(/Claude Sonnet 4/i);
      await user.click(claudeOption);

      // Model should be updated
      expect(screen.getByText(/Claude Sonnet 4/i)).toBeInTheDocument();
    });
  });

  describe('Save Functionality', () => {
    it('should call onSave with updated configuration', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const editor = screen.getByTestId('monaco-editor');
      await user.clear(editor);
      await user.type(editor, 'Updated prompt');

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledWith(
          expect.objectContaining({
            stage_1_prompt: 'Updated prompt',
          })
        );
      });
    });

    it('should disable save button while saving', async () => {
      const user = userEvent.setup();
      mockOnSave.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      expect(saveButton).toBeDisabled();

      await waitFor(() => {
        expect(saveButton).not.toBeDisabled();
      });
    });

    it('should show success message after save', async () => {
      const user = userEvent.setup();
      mockOnSave.mockResolvedValueOnce(undefined);

      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/saved successfully/i)).toBeInTheDocument();
      });
    });

    it('should show error message on save failure', async () => {
      const user = userEvent.setup();
      mockOnSave.mockRejectedValueOnce(new Error('Save failed'));

      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });
    });
  });

  describe('Validation', () => {
    it('should require all stage prompts to be non-empty', async () => {
      const user = userEvent.setup();
      render(<PromptEditor onSave={mockOnSave} />);

      const editor = screen.getByTestId('monaco-editor');
      await user.clear(editor);

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      expect(mockOnSave).not.toHaveBeenCalled();
      expect(screen.getByText(/required/i)).toBeInTheDocument();
    });

    it('should validate configuration name', async () => {
      const user = userEvent.setup();
      render(<PromptEditor onSave={mockOnSave} />);

      const nameInput = screen.getByLabelText(/configuration name/i);
      await user.clear(nameInput);

      const saveButton = screen.getByRole('button', { name: /Save/i });
      await user.click(saveButton);

      expect(mockOnSave).not.toHaveBeenCalled();
    });
  });

  describe('Cost Estimation Integration', () => {
    it('should show cost estimator', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByText(/estimated cost/i)).toBeInTheDocument();
    });

    it('should update cost estimate when model changes', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const initialCost = screen.getByTestId('estimated-cost').textContent;

      // Change model to more expensive one
      await user.click(screen.getByRole('tab', { name: /Stage 4/ }));
      const modelSelector = screen.getByRole('combobox');
      await user.click(modelSelector);
      await user.click(screen.getByText(/Claude Sonnet 4/i));

      await waitFor(() => {
        const newCost = screen.getByTestId('estimated-cost').textContent;
        expect(newCost).not.toBe(initialCost);
      });
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should save on Ctrl+S / Cmd+S', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      await user.keyboard('{Meta>}s{/Meta}');

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalled();
      });
    });

    it('should navigate stages with Ctrl+Number', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      await user.keyboard('{Control>}3{/Control}');

      const stage3Tab = screen.getByRole('tab', { name: /Stage 3/ });
      expect(stage3Tab).toHaveAttribute('data-state', 'active');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      expect(screen.getByRole('tablist')).toBeInTheDocument();
      expect(screen.getAllByRole('tab')).toHaveLength(5);
    });

    it('should support keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<PromptEditor initialConfig={mockConfig} onSave={mockOnSave} />);

      const stage1Tab = screen.getByRole('tab', { name: /Stage 1/ });
      stage1Tab.focus();

      await user.keyboard('{ArrowRight}');

      const stage2Tab = screen.getByRole('tab', { name: /Stage 2/ });
      expect(stage2Tab).toHaveFocus();
    });
  });
});

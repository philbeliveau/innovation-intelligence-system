import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { usePromptEditorStore } from '@/stores/prompt-editor-store';

describe('PromptEditorStore', () => {
  beforeEach(() => {
    const { result } = renderHook(() => usePromptEditorStore());
    act(() => {
      result.current.reset();
    });
  });

  describe('Initialization', () => {
    it('should initialize with default state', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      expect(result.current.currentConfig).toBeNull();
      expect(result.current.isDirty).toBe(false);
      expect(result.current.activeStage).toBe(1);
    });
  });

  describe('Configuration Management', () => {
    it('should set current configuration', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        name: 'Test Config',
        stage_1_prompt: 'Test prompt',
        default_model_id: 'deepseek-chat',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
      });

      expect(result.current.currentConfig).toEqual(mockConfig);
    });

    it('should update stage prompt', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Original prompt',
        stage_2_prompt: 'Stage 2',
        default_model_id: 'deepseek-chat',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.updateStagePrompt(1, 'Updated prompt');
      });

      expect(result.current.currentConfig?.stage_1_prompt).toBe('Updated prompt');
      expect(result.current.isDirty).toBe(true);
    });

    it('should update model for stage', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        default_model_id: 'deepseek-chat',
        stage_model_overrides: {},
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.updateStageModel(4, 'claude-sonnet-4');
      });

      expect(result.current.currentConfig?.stage_model_overrides?.stage_4).toBe(
        'claude-sonnet-4'
      );
      expect(result.current.isDirty).toBe(true);
    });

    it('should clear model override', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        default_model_id: 'deepseek-chat',
        stage_model_overrides: { stage_4: 'claude-sonnet-4' },
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.clearStageModelOverride(4);
      });

      expect(result.current.currentConfig?.stage_model_overrides?.stage_4).toBeUndefined();
    });
  });

  describe('Stage Navigation', () => {
    it('should set active stage', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.setActiveStage(3);
      });

      expect(result.current.activeStage).toBe(3);
    });

    it('should navigate to next stage', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.setActiveStage(2);
        result.current.nextStage();
      });

      expect(result.current.activeStage).toBe(3);
    });

    it('should not navigate beyond stage 5', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.setActiveStage(5);
        result.current.nextStage();
      });

      expect(result.current.activeStage).toBe(5);
    });

    it('should navigate to previous stage', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.setActiveStage(3);
        result.current.previousStage();
      });

      expect(result.current.activeStage).toBe(2);
    });

    it('should not navigate below stage 1', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.setActiveStage(1);
        result.current.previousStage();
      });

      expect(result.current.activeStage).toBe(1);
    });
  });

  describe('Dirty State Tracking', () => {
    it('should mark as dirty when prompt changes', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Original',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.updateStagePrompt(1, 'Modified');
      });

      expect(result.current.isDirty).toBe(true);
    });

    it('should mark as dirty when model changes', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        default_model_id: 'deepseek-chat',
        stage_model_overrides: {},
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.updateStageModel(4, 'claude-sonnet-4');
      });

      expect(result.current.isDirty).toBe(true);
    });

    it('should clear dirty state after save', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Test',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.updateStagePrompt(1, 'Modified');
        result.current.markSaved();
      });

      expect(result.current.isDirty).toBe(false);
    });
  });

  describe('Validation', () => {
    it('should validate that all stage prompts are present', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const incompleteConfig = {
        id: 'config-1',
        stage_1_prompt: 'Test',
        stage_2_prompt: '',
        stage_3_prompt: 'Test',
        stage_4_prompt: 'Test',
        stage_5_prompt: 'Test',
      };

      act(() => {
        result.current.setCurrentConfig(incompleteConfig as any);
      });

      expect(result.current.isValid()).toBe(false);
    });

    it('should validate complete configuration', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const completeConfig = {
        id: 'config-1',
        name: 'Test Config',
        stage_1_prompt: 'Test 1',
        stage_2_prompt: 'Test 2',
        stage_3_prompt: 'Test 3',
        stage_4_prompt: 'Test 4',
        stage_5_prompt: 'Test 5',
        default_model_id: 'deepseek-chat',
      };

      act(() => {
        result.current.setCurrentConfig(completeConfig as any);
      });

      expect(result.current.isValid()).toBe(true);
    });
  });

  describe('Reset', () => {
    it('should reset to initial state', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Test',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.setActiveStage(3);
        result.current.updateStagePrompt(1, 'Modified');
        result.current.reset();
      });

      expect(result.current.currentConfig).toBeNull();
      expect(result.current.activeStage).toBe(1);
      expect(result.current.isDirty).toBe(false);
    });
  });

  describe('Persistence', () => {
    it('should persist to localStorage', () => {
      const { result } = renderHook(() => usePromptEditorStore());

      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Test',
      };

      act(() => {
        result.current.setCurrentConfig(mockConfig as any);
        result.current.persistDraft();
      });

      const stored = localStorage.getItem('prompt-editor-draft');
      expect(stored).toBeTruthy();
    });

    it('should restore from localStorage', () => {
      const mockConfig = {
        id: 'config-1',
        stage_1_prompt: 'Test',
      };

      localStorage.setItem('prompt-editor-draft', JSON.stringify(mockConfig));

      const { result } = renderHook(() => usePromptEditorStore());

      act(() => {
        result.current.restoreDraft();
      });

      expect(result.current.currentConfig).toEqual(mockConfig);
    });
  });
});

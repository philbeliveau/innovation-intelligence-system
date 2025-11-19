# 8. Frontend Architecture

## Next.js 14 App Router Pattern

**Server Components (Default)**:
- `/prompts/page.tsx` - List configurations (fetch from DB)
- `/results/[runId]/page.tsx` - Display results (fetch from Blob + DB)
- Root layouts with static content

**Client Components** (`'use client'`):
- `/prompts/new/page.tsx` - Prompt editor (Monaco requires browser)
- `/run/page.tsx` - Test execution (real-time polling)
- `/comparison/page.tsx` - Brand comparison (interactive UI)
- All components using Zustand stores

## State Management Strategy

**Zustand Store - Prompt Editor**:

```typescript
// stores/prompt-editor-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PromptEditorState {
  draftConfig: PromptConfiguration | null;
  activeStage: number;

  setDraftConfig: (config: PromptConfiguration) => void;
  updateStagePrompt: (stage: number, prompt: string) => void;
  setActiveStage: (stage: number) => void;
  clearDraft: () => void;
}

export const usePromptEditorStore = create<PromptEditorState>()(
  persist(
    (set) => ({
      draftConfig: null,
      activeStage: 1,

      setDraftConfig: (config) => set({ draftConfig: config }),

      updateStagePrompt: (stage, prompt) =>
        set((state) => ({
          draftConfig: state.draftConfig
            ? {
                ...state.draftConfig,
                [`stage_${stage}_prompt`]: prompt,
              }
            : null,
        })),

      setActiveStage: (stage) => set({ activeStage: stage }),

      clearDraft: () => set({ draftConfig: null }),
    }),
    {
      name: 'prompt-editor-storage',
    }
  )
);
```

**Zustand Store - Execution Polling**:

```typescript
// stores/execution-store.ts
import { create } from 'zustand';

interface ExecutionState {
  activeRuns: Map<string, TestRun>;

  addRun: (runId: string, initialData: TestRun) => void;
  updateRun: (runId: string, data: Partial<TestRun>) => void;
  removeRun: (runId: string) => void;
}

export const useExecutionStore = create<ExecutionState>((set) => ({
  activeRuns: new Map(),

  addRun: (runId, initialData) =>
    set((state) => ({
      activeRuns: new Map(state.activeRuns).set(runId, initialData),
    })),

  updateRun: (runId, data) =>
    set((state) => {
      const newRuns = new Map(state.activeRuns);
      const existing = newRuns.get(runId);
      if (existing) {
        newRuns.set(runId, { ...existing, ...data });
      }
      return { activeRuns: newRuns };
    }),

  removeRun: (runId) =>
    set((state) => {
      const newRuns = new Map(state.activeRuns);
      newRuns.delete(runId);
      return { activeRuns: newRuns };
    }),
}));
```

## Routing Structure

```
/ (homepage)
├── /prompts (list all configurations)
│   ├── /new (create new prompt config)
│   └── /[id] (view/edit existing)
│       └── /run (execute test with this config)
├── /run (quick test execution)
├── /results/[runId] (view test results)
├── /comparison (side-by-side brand comparison)
└── /admin
    └── /costs (cost monitoring dashboard)
```

---

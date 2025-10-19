# 11. Testing Strategy

## Test Pyramid

```
        ┌─────────────────┐
        │   E2E Tests     │  20% - Critical user journeys
        │   (Playwright)   │
        ├─────────────────┤
        │ Integration Tests│  30% - API + DB + Blob
        │  (Vitest + MSW)  │
        ├─────────────────┤
        │   Unit Tests     │  50% - Business logic
        │     (Vitest)     │
        └─────────────────┘
```

## Frontend Unit Tests

**File**: `apps/web/__tests__/lib/cost-estimator.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { estimateCost } from '@/lib/cost-estimator';

describe('Cost Estimator', () => {
  it('calculates cost for single model across all stages', () => {
    const result = estimateCost({
      model_id: 'deepseek/deepseek-chat',
      num_runs: 1,
    });

    expect(result.total_cost_usd).toBeGreaterThan(0);
    expect(result.per_stage_costs.stage_1).toBeGreaterThan(0);
    expect(result.breakdown).toHaveLength(5);
  });

  it('applies per-stage model overrides correctly', () => {
    const result = estimateCost({
      model_id: 'deepseek/deepseek-chat',
      stage_model_overrides: {
        stage_4: 'anthropic/claude-sonnet-4-20250514',
      },
      num_runs: 1,
    });

    expect(result.per_stage_costs.stage_4).toBeGreaterThan(
      result.per_stage_costs.stage_1
    );
  });
});
```

## Backend Unit Tests

**File**: `api/python/tests/test_research_loader.py`

```python
import pytest
from pipeline.research_loader import ResearchDataLoader

def test_parse_research_file_success(sample_research_markdown, tmp_path):
    research_file = tmp_path / "lactalis-canada-research.md"
    research_file.write_text(sample_research_markdown)

    loader = ResearchDataLoader()
    result = loader._parse_research_file(str(research_file), "lactalis-canada")

    assert result.brand_id == "lactalis-canada"
    assert len(result.sections) == 8
    assert result.total_data_points > 0
```

## E2E Tests

**File**: `apps/web/e2e/prompt-editing-workflow.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test('user can create, save, and execute prompt configuration', async ({ page }) => {
  await page.goto('/prompts/new');

  // Edit Stage 1 prompt
  await page.getByRole('tab', { name: 'Stage 1' }).click();
  await page.getByRole('textbox').fill('Extract key insights...');

  // Save configuration
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText(/saved successfully/i)).toBeVisible();

  // Execute test
  await page.getByRole('button', { name: 'Run Test' }).click();
  await expect(page.getByText(/Completed/i)).toBeVisible({ timeout: 300000 });
});
```

---

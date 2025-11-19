# 13. Coding Standards

## Overview

Coding standards ensure consistency, maintainability, and quality across the fullstack application. These standards apply to both TypeScript/JavaScript (frontend) and Python (backend) codebases.

---

## TypeScript/JavaScript Standards

### File Organization

```typescript
// Standard file structure for components
// components/prompt-editor/PromptEditor.tsx

'use client'; // Only if Client Component

import { useState } from 'react'; // React imports first
import { Card } from '@/components/ui/card'; // Internal UI components
import { ApiClient } from '@/lib/api-client'; // Libraries
import type { PromptConfiguration } from '@/types'; // Types last

interface PromptEditorProps { // Props interface before component
  config: PromptConfiguration;
  onSave: (config: PromptConfiguration) => Promise<void>;
}

export function PromptEditor({ config, onSave }: PromptEditorProps) {
  // Component implementation
}
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Components | PascalCase | `PromptEditor`, `ExecutionMonitor` |
| Hooks | camelCase with `use` prefix | `usePromptEditor`, `useExecutionStore` |
| Utilities | camelCase | `estimateCost`, `formatCurrency` |
| Constants | SCREAMING_SNAKE_CASE | `AVAILABLE_MODELS`, `MAX_RETRIES` |
| Types/Interfaces | PascalCase | `TestRun`, `PromptConfiguration` |
| Files | kebab-case | `prompt-editor.tsx`, `cost-estimator.ts` |

### TypeScript Best Practices

```typescript
// ✅ Good: Explicit return types for functions
export function estimateCost(params: CostParams): CostEstimation {
  // ...
}

// ❌ Bad: Implicit return type
export function estimateCost(params: CostParams) {
  // ...
}

// ✅ Good: Avoid `any`, use `unknown` if truly dynamic
function processData(data: unknown): void {
  if (typeof data === 'string') {
    // Type narrowing
  }
}

// ❌ Bad: Using `any`
function processData(data: any): void {
  // ...
}

// ✅ Good: Prefer interfaces over types for object shapes
interface User {
  id: string;
  name: string;
}

// ✅ Good: Use types for unions/aliases
type Status = 'pending' | 'running' | 'completed' | 'failed';

// ✅ Good: Exhaustive switch statements
function handleStatus(status: Status): string {
  switch (status) {
    case 'pending':
      return 'Waiting to start';
    case 'running':
      return 'In progress';
    case 'completed':
      return 'Done';
    case 'failed':
      return 'Error occurred';
    default:
      const _exhaustive: never = status;
      throw new Error(`Unhandled status: ${_exhaustive}`);
  }
}
```

### React Patterns

```typescript
// ✅ Good: Use Server Components by default
export default async function ResultsPage({ params }: { params: { runId: string } }) {
  const results = await getResults(params.runId); // Server-side fetch
  return <OpportunityGrid opportunities={results.opportunities} />;
}

// ✅ Good: Client Components only when needed
'use client';

export function ExecutionMonitor({ runId }: { runId: string }) {
  const [status, setStatus] = useState<TestRun | null>(null);
  // Real-time polling requires client-side state
}

// ✅ Good: Extract complex logic to custom hooks
function useExecutionPolling(runId: string) {
  const [status, setStatus] = useState<TestRun | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const poll = async () => {
      try {
        const result = await api.getStatus(runId);
        setStatus(result);
      } catch (err) {
        setError(err as Error);
      }
    };

    const interval = setInterval(poll, 2000);
    poll();

    return () => clearInterval(interval);
  }, [runId]);

  return { status, error };
}

// ✅ Good: Memoize expensive computations
const expensiveCalculation = useMemo(() => {
  return opportunities.map(opp => calculateROI(opp));
}, [opportunities]);
```

### Error Handling

```typescript
// ✅ Good: Type-safe error handling
try {
  await api.executeTest(params);
} catch (error) {
  if (error instanceof ApiError) {
    logger.error('API request failed', { code: error.code, message: error.message });
  } else if (error instanceof Error) {
    logger.error('Unexpected error', { message: error.message });
  } else {
    logger.error('Unknown error', { error });
  }
}

// ✅ Good: Custom error classes
class ApiError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ✅ Good: Result types for expected failures
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function validatePrompt(prompt: string): Result<string, ValidationError> {
  if (prompt.length === 0) {
    return { success: false, error: new ValidationError('Prompt cannot be empty') };
  }
  return { success: true, data: prompt };
}
```

---

## Python Standards

### File Organization

```python
# pipeline/stages/stage4_brand_contextualization.py

"""
Stage 4: Brand Contextualization

Injects comprehensive brand research into general opportunities
to create brand-specific innovation insights.
"""

# Standard library imports
import json
import time
from typing import Dict, Any

# Third-party imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# Local imports
from pipeline.llm_client import create_llm_client
from pipeline.blob_client import BlobClient
from pipeline.research_loader import ResearchDataLoader
from pipeline.logger import logger


def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute Stage 4 of the pipeline."""
    # Implementation
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Functions | snake_case | `execute_stage4`, `load_research` |
| Classes | PascalCase | `ResearchDataLoader`, `BlobClient` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRIES`, `SECTION_MAP` |
| Private methods | _leading_underscore | `_parse_markdown`, `_count_data_points` |
| Files | snake_case | `stage4_brand_contextualization.py` |

### Type Hints

```python
# ✅ Good: Use type hints for all function signatures
from typing import Dict, List, Optional, Any

def execute_stage(
    run_id: str,
    input_data: Dict[str, Any],
    llm_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute pipeline stage with full type hints."""
    pass

# ✅ Good: Use dataclasses for structured data
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ResearchSection:
    title: str
    content: str
    data_points: int

@dataclass
class BrandResearch:
    brand_id: str
    sections: Dict[str, ResearchSection]
    research_date: datetime
    total_data_points: int

# ✅ Good: Use Optional for nullable values
def load_cache(key: str) -> Optional[Dict[str, Any]]:
    cache = get_cache()
    return cache.get(key)  # Returns None if not found
```

### Error Handling

```python
# ✅ Good: Specific exception types
class ResearchNotFoundError(Exception):
    """Raised when brand research file is not found."""
    def __init__(self, brand_id: str):
        self.brand_id = brand_id
        super().__init__(f"Research not found for brand: {brand_id}")

class StageExecutionError(Exception):
    """Raised when a pipeline stage fails."""
    def __init__(self, stage: int, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"Stage {stage} failed: {reason}")

# ✅ Good: Try-except with specific handling
def execute_stage(run_id: str, config: dict) -> dict:
    try:
        result = process_data(config)
        return result
    except ResearchNotFoundError as e:
        logger.error(f"Missing research data", brand_id=e.brand_id)
        raise
    except LLMTimeoutError as e:
        logger.error(f"LLM request timed out", timeout=e.timeout)
        raise StageExecutionError(stage=4, reason="LLM timeout")
    except Exception as e:
        logger.error(f"Unexpected error in stage execution", error=str(e))
        raise

# ✅ Good: Context managers for cleanup
from contextlib import contextmanager

@contextmanager
def stage_execution_context(run_id: str, stage: int):
    """Context manager for stage execution with automatic cleanup."""
    logger.stage_start(run_id, stage)
    start_time = time.time()

    try:
        yield
    except Exception as e:
        logger.error(f"Stage {stage} failed", run_id=run_id, error=str(e))
        raise
    finally:
        duration = (time.time() - start_time) * 1000
        logger.stage_complete(run_id, stage, duration_ms=duration)
```

### Docstrings

```python
# ✅ Good: Google-style docstrings
def execute_stage4(
    run_id: str,
    brand_id: str,
    stage3_output_path: str,
    prompt: str,
    llm_config: dict
) -> dict:
    """
    Execute Stage 4: Brand Contextualization.

    Loads comprehensive brand research (8 sections, 120+ data points)
    and injects it into the prompt to contextualize general opportunities
    for the specific brand.

    Args:
        run_id: Unique identifier for the test run
        brand_id: Brand identifier (e.g., "lactalis-canada")
        stage3_output_path: Blob storage path to Stage 3 output
        prompt: User-defined prompt template for Stage 4
        llm_config: LLM configuration dict with 'model' and 'temperature'

    Returns:
        dict containing:
            - output_path: Blob storage path to Stage 4 output
            - tokens_used: Total tokens consumed
            - cost_usd: Actual cost in USD

    Raises:
        ResearchNotFoundError: If brand research file is missing
        StageExecutionError: If LLM execution fails
    """
    # Implementation
```

---

## Code Quality Tools

### TypeScript/JavaScript

**ESLint Configuration** (`.eslintrc.json`):

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "react-hooks/exhaustive-deps": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  }
}
```

**Prettier Configuration** (`.prettierrc`):

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

### Python

**Ruff Configuration** (`pyproject.toml`):

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["pipeline"]
```

**mypy Configuration** (`pyproject.toml`):

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## Critical Coding Rules

### Security

```typescript
// ✅ Good: Never log sensitive data
logger.info('User authenticated', { userId: user.id }); // OK

// ❌ Bad: Logging API keys or tokens
logger.info('API call', { apiKey: process.env.OPENROUTER_API_KEY }); // NEVER

// ✅ Good: Validate all user inputs
const validateRunId = (id: string): boolean => {
  return /^[a-zA-Z0-9-]{36}$/.test(id); // UUID format
};

// ✅ Good: Use environment variables for secrets
const apiKey = process.env.OPENROUTER_API_KEY;
if (!apiKey) {
  throw new Error('OPENROUTER_API_KEY is required');
}
```

### Performance

```typescript
// ✅ Good: Avoid N+1 queries
const runs = await db.query.testRuns.findMany({
  with: {
    opportunities: true, // Load with JOIN
  },
});

// ❌ Bad: N+1 query
const runs = await db.query.testRuns.findMany();
for (const run of runs) {
  const opportunities = await db.query.opportunityCards.findMany({
    where: eq(opportunityCards.runId, run.id),
  });
}

// ✅ Good: Debounce API calls
const debouncedEstimate = useMemo(
  () => debounce((config: PromptConfiguration) => {
    estimateCost(config);
  }, 500),
  []
);
```

### Maintainability

```typescript
// ✅ Good: Single Responsibility Principle
function ExecutionMonitor({ runId }: { runId: string }) {
  const { status, error } = useExecutionPolling(runId); // Separate hook

  if (error) return <ErrorDisplay error={error} />; // Separate component
  if (!status) return <LoadingSpinner />;

  return <StageProgressList stages={status.stages} />;
}

// ✅ Good: Avoid magic numbers
const POLLING_INTERVAL_MS = 2000;
const MAX_RETRIES = 3;
const STAGE_TIMEOUT_MS = 300000; // 5 minutes

// ❌ Bad: Magic numbers
setInterval(poll, 2000); // What is 2000?
```

---

## Git Commit Standards

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat: New feature
fix: Bug fix
docs: Documentation changes
style: Formatting, missing semicolons, etc.
refactor: Code restructuring without behavior change
test: Adding tests
chore: Build process, dependencies, etc.

# Examples:
feat(prompt-editor): add Monaco syntax highlighting
fix(stage4): handle missing research data gracefully
docs(architecture): complete coding standards section
refactor(cost-estimator): extract token calculation logic
test(research-loader): add parsing edge cases
```

---

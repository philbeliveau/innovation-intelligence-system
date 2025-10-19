# 14. Error Handling Strategy

## Overview

The Innovation Intelligence Pipeline requires robust error handling across three layers:
1. **User-Facing Errors** - Clear, actionable messages in the UI
2. **System Errors** - Logged for debugging and monitoring
3. **Recovery Strategies** - Automatic retries and fallbacks

---

## Error Classification

| Error Type | User Impact | Recovery Strategy | Example |
|------------|-------------|-------------------|---------|
| **Validation Error** | Immediate feedback | User corrects input | Empty prompt field |
| **Client Error (4xx)** | Actionable message | User fixes request | Invalid brand ID |
| **Server Error (5xx)** | Retry option | Automatic retry (3x) | LLM API timeout |
| **Network Error** | Retry option | Exponential backoff | Connection lost |
| **Data Not Found** | Informative message | Suggest alternatives | Missing research file |

---

## Frontend Error Handling

### API Error Types

```typescript
// lib/errors.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, public field: string) {
    super(message, 400, 'VALIDATION_ERROR', { field });
  }
}

export class ResourceNotFoundError extends ApiError {
  constructor(resourceType: string, resourceId: string) {
    super(
      `${resourceType} not found: ${resourceId}`,
      404,
      'RESOURCE_NOT_FOUND',
      { resourceType, resourceId }
    );
  }
}

export class LLMTimeoutError extends ApiError {
  constructor(stage: number, timeout: number) {
    super(
      `Stage ${stage} timed out after ${timeout}ms`,
      504,
      'LLM_TIMEOUT',
      { stage, timeout }
    );
  }
}

export class InsufficientCreditsError extends ApiError {
  constructor(required: number, available: number) {
    super(
      `Insufficient credits: ${available} available, ${required} required`,
      402,
      'INSUFFICIENT_CREDITS',
      { required, available }
    );
  }
}
```

### Error Boundary Component

```typescript
// components/ErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { logger } from '@/lib/logger';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    logger.error('Uncaught error in component tree', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
    });
  }

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, () =>
          this.setState({ hasError: false, error: null })
        );
      }

      return (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Something went wrong</AlertTitle>
          <AlertDescription>
            {this.state.error.message}
            <Button
              variant="outline"
              size="sm"
              className="mt-2"
              onClick={() => this.setState({ hasError: false, error: null })}
            >
              Try again
            </Button>
          </AlertDescription>
        </Alert>
      );
    }

    return this.props.children;
  }
}
```

### API Client with Error Handling

```typescript
// lib/api-client.ts
export class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Handle different error types
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        switch (response.status) {
          case 400:
            throw new ValidationError(
              errorData.message || 'Validation failed',
              errorData.field
            );
          case 404:
            throw new ResourceNotFoundError(
              errorData.resourceType || 'Resource',
              errorData.resourceId || 'unknown'
            );
          case 402:
            throw new InsufficientCreditsError(
              errorData.required,
              errorData.available
            );
          case 504:
            throw new LLMTimeoutError(errorData.stage, errorData.timeout);
          default:
            throw new ApiError(
              errorData.message || 'Request failed',
              response.status,
              errorData.code || 'UNKNOWN_ERROR',
              errorData
            );
        }
      }

      return response.json();
    } catch (error) {
      // Network errors
      if (error instanceof TypeError) {
        throw new ApiError(
          'Network error - check your connection',
          0,
          'NETWORK_ERROR'
        );
      }

      // Re-throw API errors
      throw error;
    }
  }

  // Usage with retry logic
  async executeTest(params: ExecuteTestParams): Promise<{ run_id: string }> {
    return this.withRetry(() => this.request('/pipeline/execute', {
      method: 'POST',
      body: JSON.stringify(params),
    }));
  }

  private async withRetry<T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
  ): Promise<T> {
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Don't retry validation errors or 4xx errors
        if (error instanceof ValidationError ||
            (error instanceof ApiError && error.statusCode < 500)) {
          throw error;
        }

        if (attempt < maxRetries) {
          await new Promise(resolve => setTimeout(resolve, delay * (attempt + 1)));
        }
      }
    }

    throw lastError!;
  }
}
```

### User-Facing Error Messages

```typescript
// lib/error-messages.ts
export function getUserFriendlyMessage(error: Error): {
  title: string;
  message: string;
  action?: string;
} {
  if (error instanceof ValidationError) {
    return {
      title: 'Validation Error',
      message: error.message,
      action: `Please check the ${error.field} field and try again.`,
    };
  }

  if (error instanceof ResourceNotFoundError) {
    return {
      title: 'Not Found',
      message: `The requested ${error.details.resourceType} could not be found.`,
      action: 'Please check the ID and try again, or select from available options.',
    };
  }

  if (error instanceof LLMTimeoutError) {
    return {
      title: 'Processing Timeout',
      message: `Stage ${error.details.stage} is taking longer than expected.`,
      action: 'This sometimes happens with complex prompts. Try again or use a different model.',
    };
  }

  if (error instanceof InsufficientCreditsError) {
    return {
      title: 'Insufficient Credits',
      message: `This test requires $${error.details.required.toFixed(2)}, but you have $${error.details.available.toFixed(2)} available.`,
      action: 'Add credits to your account or use a cheaper model.',
    };
  }

  if (error instanceof ApiError && error.code === 'NETWORK_ERROR') {
    return {
      title: 'Connection Error',
      message: 'Unable to reach the server.',
      action: 'Check your internet connection and try again.',
    };
  }

  return {
    title: 'Unexpected Error',
    message: error.message,
    action: 'If this persists, please contact support.',
  };
}
```

---

## Backend Error Handling

### Python Exception Hierarchy

```python
# pipeline/exceptions.py
class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    def __init__(self, message: str, stage: int = None, details: dict = None):
        self.message = message
        self.stage = stage
        self.details = details or {}
        super().__init__(message)

class ResearchNotFoundError(PipelineError):
    """Raised when brand research file is not found."""
    def __init__(self, brand_id: str):
        super().__init__(
            f"Research not found for brand: {brand_id}",
            details={'brand_id': brand_id, 'resource_type': 'brand_research'}
        )

class LLMTimeoutError(PipelineError):
    """Raised when LLM request exceeds timeout."""
    def __init__(self, stage: int, timeout: int):
        super().__init__(
            f"LLM request timed out after {timeout}ms",
            stage=stage,
            details={'timeout': timeout}
        )

class LLMAPIError(PipelineError):
    """Raised when LLM API returns an error."""
    def __init__(self, stage: int, status_code: int, error_message: str):
        super().__init__(
            f"LLM API error: {error_message}",
            stage=stage,
            details={'status_code': status_code, 'api_message': error_message}
        )

class InvalidPromptError(PipelineError):
    """Raised when prompt template is invalid."""
    def __init__(self, stage: int, reason: str):
        super().__init__(
            f"Invalid prompt for stage {stage}: {reason}",
            stage=stage,
            details={'reason': reason}
        )
```

### Retry Decorator

```python
# pipeline/utils.py
import time
import functools
from typing import Callable, Type, Tuple

def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exception types to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1} failed, retrying in {current_delay}s",
                            error=str(e),
                            function=func.__name__
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed",
                            error=str(e),
                            function=func.__name__
                        )

            raise last_exception

        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=2.0, exceptions=(LLMAPIError, LLMTimeoutError))
def call_llm_api(prompt: str, config: dict) -> str:
    response = llm.invoke(prompt)
    return response.content
```

### Stage Execution Error Handling

```python
# pipeline/stages/base.py
from contextlib import contextmanager
from typing import Generator

@contextmanager
def stage_execution(
    run_id: str,
    stage: int,
    model: str
) -> Generator[None, None, None]:
    """Context manager for stage execution with comprehensive error handling."""
    logger.stage_start(run_id, stage, model)
    start_time = time.time()

    try:
        yield

        duration_ms = (time.time() - start_time) * 1000
        logger.stage_complete(run_id, stage, duration_ms=duration_ms)

    except ResearchNotFoundError as e:
        logger.error(
            f"Research data missing for stage {stage}",
            run_id=run_id,
            stage=stage,
            brand_id=e.details.get('brand_id')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Missing research data: {e.message}")
        raise

    except LLMTimeoutError as e:
        logger.error(
            f"LLM timeout in stage {stage}",
            run_id=run_id,
            stage=stage,
            timeout=e.details.get('timeout')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Stage {stage} timed out")
        raise

    except LLMAPIError as e:
        logger.error(
            f"LLM API error in stage {stage}",
            run_id=run_id,
            stage=stage,
            status_code=e.details.get('status_code'),
            api_message=e.details.get('api_message')
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"LLM API error: {e.message}")
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error in stage {stage}",
            run_id=run_id,
            stage=stage,
            error=str(e),
            error_type=type(e).__name__
        )
        # Update DB: mark run as failed
        update_run_status(run_id, 'failed', f"Unexpected error: {str(e)}")
        raise PipelineError(f"Stage {stage} failed", stage=stage, details={'error': str(e)})

# Usage in stage function
def execute_stage4(run_id: str, brand_id: str, ...) -> dict:
    with stage_execution(run_id, stage=4, model=llm_config['model']):
        # Load research
        research = research_loader.get_brand_research(brand_id)

        # Execute LLM with retry
        response = call_llm_api(formatted_prompt, llm_config)

        # Save output
        blob_client.write(output_path, response)

        return {'output_path': output_path, ...}
```

---

## Error Recovery Strategies

### Graceful Degradation

```typescript
// If cost estimation fails, show approximate cost
async function estimateWithFallback(config: PromptConfiguration): Promise<number> {
  try {
    const estimate = await api.estimateCost(config);
    return estimate.total_cost_usd;
  } catch (error) {
    logger.warn('Cost estimation failed, using approximate value', { error });
    // Fallback: Use average cost based on model
    return getApproximateCost(config.default_model_id);
  }
}
```

### Partial Failure Handling

```python
# If one opportunity card generation fails, continue with others
def generate_opportunity_cards(opportunities: List[dict]) -> List[OpportunityCard]:
    cards = []
    errors = []

    for idx, opp in enumerate(opportunities):
        try:
            card = render_opportunity_card(opp, idx + 1)
            cards.append(card)
        except Exception as e:
            logger.error(f"Failed to generate card {idx + 1}", error=str(e))
            errors.append((idx + 1, str(e)))
            # Continue with next card

    if len(cards) == 0:
        raise PipelineError(f"All opportunity card generation failed: {errors}")

    if errors:
        logger.warning(f"Generated {len(cards)}/5 cards successfully", errors=errors)

    return cards
```

---

## Error Monitoring & Alerting

```typescript
// Send critical errors to Sentry with context
function reportCriticalError(error: Error, context: Record<string, any>) {
  Sentry.captureException(error, {
    level: 'error',
    contexts: {
      pipeline: context,
    },
    tags: {
      error_type: error.constructor.name,
      component: context.component || 'unknown',
    },
  });
}

// Usage
try {
  await api.executeTest(params);
} catch (error) {
  reportCriticalError(error as Error, {
    component: 'ExecutionMonitor',
    run_id: runId,
    brand_id: params.brand_id,
    prompt_config_id: params.prompt_config_id,
  });
  throw error;
}
```

---

**Rationale for Error Handling Decisions**:

1. **Typed errors**: TypeScript classes enable compile-time checking and better autocomplete
2. **User-friendly messages**: Non-technical language with actionable next steps
3. **Automatic retries**: Transient failures (network, LLM timeouts) recovered without user intervention
4. **Graceful degradation**: Cost estimation fallback prevents UI from breaking
5. **Comprehensive logging**: All errors logged with context for debugging
6. **Error boundaries**: Prevent entire app crashes from component errors
7. **Sentry integration**: Production error tracking with full context

---

**Document Status**: ✅ All 14 sections completed.

**Last Updated**: 2025-01-XX
**Version**: 1.0 (Final Draft)

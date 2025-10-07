# 10. Error Handling

## 10.1 Error Classification

| Error Type | Severity | Handling Strategy |
|------------|----------|-------------------|
| **Missing input file** | Fatal | Halt immediately, clear error message |
| **Missing brand profile** | Fatal | Halt immediately, clear error message |
| **Missing research data** | Warning | Log warning, proceed with brand profile only |
| **LLM API timeout** | Retryable | Retry up to 3 times with exponential backoff |
| **LLM API rate limit** | Retryable | Wait and retry (respect rate limit headers) |
| **Invalid YAML syntax** | Fatal | Halt immediately, show YAML validation error |
| **Stage output empty** | Fatal | Halt immediately, log LLM response |
| **JSON parsing failure (Stage 5)** | Fatal | Halt immediately, show raw LLM output |

## 10.2 Error Handling Implementation

```python
# pipeline/utils.py

import logging
import time
from functools import wraps

def retry_on_api_error(max_retries=3, backoff_factor=2):
    """Decorator for retrying LLM API calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise

                    wait_time = backoff_factor ** attempt
                    logging.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                    logging.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        return wrapper
    return decorator

class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass

class InputError(PipelineError):
    """Error loading input document or brand profile."""
    pass

class StageExecutionError(PipelineError):
    """Error during stage execution."""
    def __init__(self, stage_num, message, llm_output=None):
        self.stage_num = stage_num
        self.llm_output = llm_output
        super().__init__(f"Stage {stage_num} failed: {message}")
```

## 10.3 Logging Configuration

```python
# pipeline/utils.py

def setup_logging(log_dir, level=logging.INFO):
    """Configure logging for pipeline execution."""
    log_dir.mkdir(parents=True, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler (detailed)
    file_handler = logging.FileHandler(log_dir / "pipeline.log")
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
```

---

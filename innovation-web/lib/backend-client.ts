/**
 * Backend API Client for Railway FastAPI Backend
 *
 * Provides typed functions to interact with the Railway-hosted pipeline backend.
 * Includes retry logic with exponential backoff for network resilience.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
const MAX_RETRIES = 3
const INITIAL_RETRY_DELAY = 1000 // 1 second

/**
 * Pipeline status response from backend
 */
export interface PipelineStatus {
  run_id: string
  status: 'running' | 'completed' | 'error'
  current_stage: number
  brand_name?: string
  stage1_data?: unknown
  error?: string
}

/**
 * Run pipeline response from backend
 */
export interface RunPipelineResponse {
  run_id: string
  status: string
}

/**
 * Exponential backoff delay calculation
 */
function getRetryDelay(attemptNumber: number): number {
  return INITIAL_RETRY_DELAY * Math.pow(2, attemptNumber)
}

/**
 * Sleep utility for retry delays
 */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Execute fetch with retry logic
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries: number = MAX_RETRIES
): Promise<Response> {
  let lastError: Error | null = null
  let lastResponse: Response | null = null

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: AbortSignal.timeout(30000), // 30 second timeout
      })

      // If response is OK or a non-retriable error (4xx), return immediately
      if (response.ok || (response.status >= 400 && response.status < 500)) {
        return response
      }

      // Store response for potential error sanitization
      lastResponse = response
      // 5xx errors are retriable
      lastError = new Error(`Server error: ${response.status}`)
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error')

      // Don't retry on timeout errors (AbortError)
      if (lastError.name === 'AbortError') {
        throw new Error('Request timeout (30s exceeded)')
      }
    }

    // Wait before retrying (except on last attempt)
    if (attempt < maxRetries - 1) {
      const delay = getRetryDelay(attempt)
      console.log(`[Backend Client] Retry attempt ${attempt + 1}/${maxRetries} after ${delay}ms`)
      await sleep(delay)
    }
  }

  // All retries exhausted - sanitize 5xx errors
  if (lastResponse && lastResponse.status >= 500) {
    throw new Error('Backend service is temporarily unavailable. Please try again later.')
  }

  throw lastError || new Error('All retry attempts failed')
}

/**
 * Trigger pipeline execution on Railway backend
 *
 * @param blobUrl - Vercel Blob URL of the uploaded PDF
 * @param brandId - Brand identifier (e.g., 'lactalis-canada')
 * @returns Run ID and initial status
 * @throws Error if backend is unreachable or returns error
 */
export async function runPipeline(
  blobUrl: string,
  brandId: string
): Promise<RunPipelineResponse> {
  // Generate unique run ID on frontend (UUID v4)
  const runId = crypto.randomUUID()

  try {
    const response = await fetchWithRetry(
      `${BACKEND_URL}/run`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blob_url: blobUrl,
          brand_id: brandId,
        }),
      }
    )

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      // Sanitize error messages to prevent internal implementation leakage
      const userFriendlyError = response.status >= 500
        ? 'Pipeline service is experiencing issues. Please try again later.'
        : errorData.error || `Request failed with status ${response.status}`
      throw new Error(userFriendlyError)
    }

    return await response.json()
  } catch (error) {
    console.error('[Backend Client] Failed to run pipeline:', error)
    throw error
  }
}

/**
 * Get pipeline execution status from Railway backend
 *
 * @param runId - Unique run identifier
 * @returns Pipeline status with current stage and data
 * @throws Error if backend is unreachable or run_id not found
 */
export async function getStatus(runId: string): Promise<PipelineStatus> {
  try {
    const response = await fetchWithRetry(
      `${BACKEND_URL}/status/${runId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Run ID not found or pipeline not started yet')
      }

      const errorData = await response.json().catch(() => ({}))
      // Sanitize error messages to prevent internal implementation leakage
      const userFriendlyError = response.status >= 500
        ? 'Pipeline status service is experiencing issues. Please try again later.'
        : errorData.error || 'Unable to fetch pipeline status'
      throw new Error(userFriendlyError)
    }

    return await response.json()
  } catch (error) {
    console.error('[Backend Client] Failed to get status:', error)
    throw error
  }
}

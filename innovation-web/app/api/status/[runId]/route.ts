import { NextRequest, NextResponse } from 'next/server'
import { readFileSync, existsSync } from 'fs'
import { join } from 'path'

/**
 * Detect current pipeline stage from log content by parsing stage start/completion messages
 *
 * @param logContent - The full content of the pipeline.log file
 * @returns Stage number (0-5): 0 = not started, 1-5 = current/completed stage
 * @example
 * ```typescript
 * const stage = detectStageFromLog(logContent)
 * // stage === 3 if log contains "Starting Stage 3" or "Stage 3 execution completed"
 * ```
 */
function detectStageFromLog(logContent: string): number {
  // Check for completion messages first (higher priority)
  if (logContent.includes('Stage 5 execution completed')) return 5
  if (logContent.includes('Stage 4 execution completed')) return 4
  if (logContent.includes('Stage 3 execution completed')) return 3
  if (logContent.includes('Stage 2 execution completed')) return 2
  if (logContent.includes('Stage 1 execution completed')) return 1

  // Check for starting messages
  if (logContent.includes('Starting Stage 5')) return 5
  if (logContent.includes('Starting Stage 4')) return 4
  if (logContent.includes('Starting Stage 3')) return 3
  if (logContent.includes('Starting Stage 2')) return 2
  if (logContent.includes('Starting Stage 1')) return 1

  // Default: pipeline not started yet
  return 0
}

/**
 * Determine pipeline execution status from log content by detecting error/completion markers
 *
 * @param logContent - The full content of the pipeline.log file
 * @returns Pipeline status: "running" (in progress), "completed" (all stages done), or "error" (failure detected)
 * @example
 * ```typescript
 * const status = detectStatusFromLog(logContent)
 * if (status === 'error') {
 *   // Handle pipeline failure
 * }
 * ```
 */
function detectStatusFromLog(logContent: string): string {
  // Check for errors
  if (
    logContent.includes('ERROR') ||
    logContent.includes('Exception') ||
    logContent.includes('failed') ||
    logContent.includes('CRITICAL')
  ) {
    return 'error'
  }

  // Check for completion
  if (logContent.includes('Stage 5 execution completed') || logContent.includes('Pipeline completed successfully')) {
    return 'completed'
  }

  // Default: still running
  return 'running'
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    // Extract runId from URL parameter
    const { runId } = await params

    // Sanitize runId to prevent path traversal
    const sanitizedRunId = runId.replace(/[^a-z0-9-]/gi, '')
    if (sanitizedRunId !== runId) {
      return NextResponse.json(
        { error: 'Invalid run ID format' },
        { status: 400 }
      )
    }

    // Get project root (go up from innovation-web)
    const projectRoot = join(process.cwd(), '..')

    // Construct log file path
    const logPath = join(
      projectRoot,
      'data',
      'test-outputs',
      sanitizedRunId,
      'logs',
      'pipeline.log'
    )

    // Check if log file exists
    if (!existsSync(logPath)) {
      return NextResponse.json(
        { error: 'Run ID not found or pipeline not started yet' },
        { status: 404 }
      )
    }

    // Read log file
    let logContent: string
    try {
      logContent = readFileSync(logPath, 'utf-8')
    } catch (error) {
      console.error(`Failed to read log file at ${logPath}:`, error)
      return NextResponse.json(
        { error: 'Failed to read pipeline logs' },
        { status: 500 }
      )
    }

    // Detect current stage and status
    const current_stage = detectStageFromLog(logContent)
    const status = detectStatusFromLog(logContent)

    // Prepare response
    const response: {
      run_id: string
      status: string
      current_stage: number
      stage1_data?: unknown
    } = {
      run_id: sanitizedRunId,
      status,
      current_stage,
    }

    // If Stage 1 is completed, try to load Stage 1 JSON data
    if (current_stage >= 1) {
      const stage1JsonPath = join(
        projectRoot,
        'data',
        'test-outputs',
        sanitizedRunId,
        'stage1',
        'inspirations.json'
      )

      if (existsSync(stage1JsonPath)) {
        try {
          const stage1Content = readFileSync(stage1JsonPath, 'utf-8')
          response.stage1_data = JSON.parse(stage1Content)
        } catch (error) {
          console.error(`Failed to read/parse Stage 1 JSON at ${stage1JsonPath}:`, error)
          // Don't fail the whole request if Stage 1 data is missing or invalid
        }
      }
    }

    return NextResponse.json(response)
  } catch (error) {
    console.error('Unexpected error in /api/status/[runId]:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

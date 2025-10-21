import { NextRequest, NextResponse } from 'next/server'
import { getStatus } from '@/lib/backend-client'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    // Extract runId from URL parameter
    const { runId } = await params

    // Sanitize runId to prevent injection attacks
    const sanitizedRunId = runId.replace(/[^a-z0-9-]/gi, '')
    if (sanitizedRunId !== runId) {
      return NextResponse.json(
        { error: 'Invalid run ID format' },
        { status: 400 }
      )
    }

    console.log(`[API /status] Fetching status for run: ${sanitizedRunId}`)

    // Call Railway backend to get status
    let statusResponse
    try {
      statusResponse = await getStatus(sanitizedRunId)
    } catch (error) {
      console.error('[API /status] Backend client error:', error)

      // Handle specific error cases
      if (error instanceof Error) {
        // 404 - Run ID not found
        if (error.message.includes('not found') || error.message.includes('404')) {
          return NextResponse.json(
            { error: 'Run ID not found or pipeline not started yet' },
            { status: 404 }
          )
        }

        // Timeout errors
        if (error.message.includes('timeout')) {
          return NextResponse.json(
            { error: 'Backend is slow to respond. Please wait and try again.' },
            { status: 504 }
          )
        }

        // Network errors
        if (error.message.includes('fetch failed') || error.message.includes('Failed to fetch')) {
          return NextResponse.json(
            { error: 'Cannot connect to backend. Please try again later.' },
            { status: 503 }
          )
        }

        // Generic backend error
        return NextResponse.json(
          { error: error.message || 'Failed to fetch pipeline status' },
          { status: 500 }
        )
      }

      // Unknown error
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      )
    }

    // Proxy Railway backend response to frontend
    console.log(`[API /status] Status: ${statusResponse.status}, Stage: ${statusResponse.current_stage}`)
    return NextResponse.json(statusResponse)
  } catch (error) {
    console.error('Unexpected error in /api/status/[runId]:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

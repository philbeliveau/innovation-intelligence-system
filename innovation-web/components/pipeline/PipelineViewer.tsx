'use client'

import { useEffect, useState } from 'react'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import StageBox from '@/components/pipeline/StageBox'
import PipelineTrackCard from '@/components/pipeline/PipelineTrackCard'
import DetailPanel from '@/components/pipeline/DetailPanel'
import { calculateStageStatus } from '@/lib/stageStatus'

interface Stage1Data {
  selected_track: 1 | 2
  track_1: {
    title: string
    summary: string
    icon_url: string
  }
  track_2: {
    title: string
    summary: string
    icon_url: string
  }
  completed_at: string
}

interface PipelineStatus {
  run_id: string
  status: 'running' | 'complete' | 'completed' | 'error' // Backend uses 'complete', frontend uses 'completed'
  current_stage: number
  stage1_data?: Stage1Data
  brand_name?: string
}

interface PipelineViewerProps {
  runId: string
  onComplete?: (runId: string) => void
  onError?: (error: string) => void
  inlineMode?: boolean
}

const stages = [
  { number: 1, name: 'Tracks', description: 'Track Division - Selected 2 inspiration tracks' },
  { number: 2, name: 'Signals', description: 'Signal Amplification - Extracting broader trends' },
  { number: 3, name: 'Lessons', description: 'Universal Translation - Converting to brand-agnostic lessons' },
  { number: 4, name: 'Context', description: 'Brand Contextualization - Applying to brand' },
  { number: 5, name: 'Opport.', description: 'Opportunity Generation - Creating 5 actionable innovations' }
]

export default function PipelineViewer({
  runId,
  onComplete,
  onError,
  inlineMode = false
}: PipelineViewerProps) {
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
  const [currentStage, setCurrentStage] = useState<number>(0)
  const [stage1Data, setStage1Data] = useState<Stage1Data | null>(null)
  const [brandName, setBrandName] = useState<string>()
  const [loading, setLoading] = useState(true)

  // Validate run ID format before starting
  useEffect(() => {
    console.log('[PipelineViewer] Component mounted with runId:', runId)
    console.log('[PipelineViewer] Inline mode:', inlineMode)

    if (!runId || runId.trim() === '') {
      const errorMsg = 'Invalid run ID provided'
      console.error('[PipelineViewer] ERROR: Invalid run ID:', runId)
      setStatus('error')
      setLoading(false)
      onError?.(errorMsg)
      return
    }
  }, [runId, onError, inlineMode])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | undefined
    let retryCount = 0
    let isFirstPoll = true
    let isCancelled = false // Track if component unmounted
    const startTime = Date.now()
    const MAX_RUNTIME = 35 * 60 * 1000 // 35 minutes
    const MAX_RETRIES = 3

    // Exponential backoff: 5s, 10s, 20s
    const getRetryDelay = (attempt: number): number => {
      return 5000 * Math.pow(2, attempt)
    }

    const pollStatus = async () => {
      // Stop polling if component unmounted
      if (isCancelled) return

      try {
        // FIX RACE-001: Add 2-second delay before first poll to let Python create log file
        if (isFirstPoll) {
          console.log('[PipelineViewer] Starting polling for runId:', runId)
          console.log('[PipelineViewer] Will poll endpoint:', `/api/pipeline/${runId}/status`)
          isFirstPoll = false
          await new Promise(resolve => setTimeout(resolve, 2000))
        }

        // Check for timeout
        const elapsed = Date.now() - startTime
        if (elapsed > MAX_RUNTIME) {
          const errorMsg = 'Pipeline timeout - exceeded 35 minutes'
          console.error('[PipelineViewer] Pipeline timeout after 35 minutes')
          setStatus('error')
          setLoading(false)
          onError?.(errorMsg)
          return
        }

        const statusUrl = `/api/pipeline/${runId}/status`
        console.log('[PipelineViewer] Polling status:', statusUrl)
        const response = await fetch(statusUrl)

        // FIX RACE-001: Treat initial 404s as "pipeline starting up" instead of error
        if (response.status === 404) {
          if (retryCount < 5) {
            // Pipeline still starting up - retry with short delay
            retryCount++
            console.log(`[PipelineViewer] Pipeline starting... retry ${retryCount}/5 for run: ${runId}`)
            timeoutId = setTimeout(pollStatus, 1000)
            return
          } else {
            // After 5 retries, treat as genuine error
            console.error(`[PipelineViewer] Run ${runId} not found on backend after 5 retries`)
            const errorMsg = `Pipeline run not found on server. Run ID: ${runId}. This usually means the pipeline was never started. Please try launching again.`
            setStatus('error')
            setLoading(false)
            onError?.(errorMsg)
            return
          }
        }

        if (!response.ok) {
          throw new Error('Failed to fetch status')
        }

        const data: PipelineStatus = await response.json()
        console.log('[PipelineViewer] Received status:', data.status, 'stage:', data.current_stage)

        // Normalize 'complete' to 'completed' for frontend state
        const normalizedStatus = data.status === 'complete' ? 'completed' : data.status
        setStatus(normalizedStatus)
        setCurrentStage(data.current_stage)
        setStage1Data(data.stage1_data ?? null)
        setBrandName(data.brand_name)
        setLoading(false)
        retryCount = 0 // Reset retry count on success

        if (data.status === 'error') {
          console.error('[PipelineViewer] Pipeline failed with error status')
          onError?.('Pipeline failed')
          return
        }

        // Handle completion (backend returns 'complete', not 'completed')
        if (data.current_stage === 5 && (data.status === 'complete' || data.status === 'completed')) {
          console.log('[PipelineViewer] Pipeline completed! Navigating to results...')
          onComplete?.(runId)
          return
        }

        // Continue polling if still running
        if (data.status === 'running') {
          console.log('[PipelineViewer] Pipeline still running, polling again in 5s')
          timeoutId = setTimeout(pollStatus, 5000)
        } else {
          console.log('[PipelineViewer] Pipeline status:', data.status, '- stopping poll')
        }
      } catch (err) {
        console.error('Polling error:', err)

        // Exponential backoff retry (3 attempts: 5s, 10s, 20s)
        if (retryCount < MAX_RETRIES) {
          const delay = getRetryDelay(retryCount)
          retryCount++
          console.log(`Retrying in ${delay}ms (attempt ${retryCount}/${MAX_RETRIES})`)
          timeoutId = setTimeout(pollStatus, delay)
        } else {
          const errorMsg = 'Network error - unable to connect to server after multiple retries'
          setStatus('error')
          setLoading(false)
          onError?.(errorMsg)
        }
      }
    }

    pollStatus()

    // Cleanup function to clear timeout on unmount
    return () => {
      isCancelled = true // Signal to stop polling
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [runId, onComplete, onError])

  // Loading state
  if (loading) {
    return (
      <div className={inlineMode ? 'space-y-4' : 'min-h-screen bg-gray-50 flex items-center justify-center'}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pipeline status...</p>
        </div>
      </div>
    )
  }

  // Get selected and non-selected tracks
  const selectedTrack = stage1Data ? (stage1Data.selected_track === 1 ? stage1Data.track_1 : stage1Data.track_2) : null
  const selectedTrackNumber = stage1Data?.selected_track

  return (
    <div className={inlineMode ? 'space-y-6' : 'min-h-screen bg-gray-50'}>
      {/* Header with Company name (only in full-page mode) */}
      {!inlineMode && (
        <div className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Pipeline Execution</h1>
              {brandName && (
                <Badge variant="secondary" className="text-sm" data-testid="company-badge">
                  {brandName}
                </Badge>
              )}
            </div>
          </div>
        </div>
      )}

      <div className={inlineMode ? '' : 'container mx-auto px-4 py-8'}>
        {/* Inline mode: Compact vertical layout */}
        {inlineMode ? (
          <div className="space-y-6">
            {/* Stage Boxes */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Pipeline Stages</h2>
              <div className="flex flex-col gap-4">
                {stages.map((stage, index) => (
                  <div key={stage.number}>
                    <StageBox
                      stageNumber={stage.number}
                      stageName={stage.name}
                      status={calculateStageStatus(stage.number, currentStage)}
                    />
                    {index < stages.length - 1 && (
                      <div className="flex justify-center py-2">
                        <div className="text-gray-400 text-2xl">↓</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Completion Message */}
            {status === 'completed' && (
              <DetailPanel
                currentStage={currentStage}
                status="complete"
                runId={runId}
                brandName={brandName}
              />
            )}
          </div>
        ) : (
          /* Full-page mode: Original 2-column layout */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left Sidebar: Stage Boxes */}
            <div className="lg:col-span-3 space-y-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4">Pipeline Stages</h2>
                <div className="flex flex-col gap-4">
                  {stages.map((stage, index) => (
                    <div key={stage.number}>
                      <StageBox
                        stageNumber={stage.number}
                        stageName={stage.name}
                        status={calculateStageStatus(stage.number, currentStage)}
                      />
                      {index < stages.length - 1 && (
                        <div className="flex justify-center py-2">
                          <div className="text-gray-400 text-2xl">↓</div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Content: Selected Track & Completion Panel */}
            <div className="lg:col-span-9">
              {/* Selected Track Card */}
              {currentStage >= 1 && (
                <div className="mb-6">
                  <h2 className="text-xl font-semibold mb-4">Selected Inspiration Track</h2>
                  {selectedTrack && selectedTrackNumber ? (
                    <PipelineTrackCard
                      trackNumber={selectedTrackNumber}
                      title={selectedTrack.title}
                      summary={selectedTrack.summary}
                    />
                  ) : currentStage === 1 ? (
                    <Skeleton className="h-48" />
                  ) : null}
                </div>
              )}

              {/* Completion Message */}
              {status === 'completed' && (
                <DetailPanel
                  currentStage={currentStage}
                  status="complete"
                  runId={runId}
                  brandName={brandName}
                />
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

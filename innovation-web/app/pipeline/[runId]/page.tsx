'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import StageBox from '@/components/pipeline/StageBox'
import PipelineTrackCard from '@/components/pipeline/PipelineTrackCard'
import IdeationTracksSidebar from '@/components/pipeline/IdeationTracksSidebar'
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
  status: 'running' | 'complete' | 'error'
  current_stage: number
  stage1_data?: Stage1Data
  brand_name?: string
}

const stages = [
  { number: 1, name: 'Tracks', description: 'Track Division - Selected 2 inspiration tracks' },
  { number: 2, name: 'Signals', description: 'Signal Amplification - Extracting broader trends' },
  { number: 3, name: 'Lessons', description: 'Universal Translation - Converting to brand-agnostic lessons' },
  { number: 4, name: 'Context', description: 'Brand Contextualization - Applying to brand' },
  { number: 5, name: 'Opport.', description: 'Opportunity Generation - Creating 5 actionable innovations' }
]

export default function PipelinePage() {
  const params = useParams()
  const router = useRouter()
  const runId = params.runId as string

  const [status, setStatus] = useState<'running' | 'complete' | 'error'>('running')
  const [currentStage, setCurrentStage] = useState<number>(0)
  const [stage1Data, setStage1Data] = useState<Stage1Data | null>(null)
  const [brandName, setBrandName] = useState<string>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | undefined
    let retryCount = 0
    const startTime = Date.now()
    const MAX_RUNTIME = 35 * 60 * 1000 // 35 minutes

    const pollStatus = async () => {
      try {
        // Check for timeout
        const elapsed = Date.now() - startTime
        if (elapsed > MAX_RUNTIME) {
          setError('Pipeline timeout - exceeded 35 minutes')
          setStatus('error')
          setLoading(false)
          return
        }

        const response = await fetch(`/api/status/${runId}`)

        if (response.status === 404) {
          setError('Pipeline not found')
          setStatus('error')
          setLoading(false)
          return
        }

        if (!response.ok) {
          throw new Error('Failed to fetch status')
        }

        const data: PipelineStatus = await response.json()

        setStatus(data.status)
        setCurrentStage(data.current_stage)
        setStage1Data(data.stage1_data ?? null)
        setBrandName(data.brand_name)
        setLoading(false)
        retryCount = 0 // Reset retry count on success

        if (data.status === 'error') {
          setError('Pipeline failed')
          return
        }

        // Auto-redirect when Stage 5 completes
        if (data.current_stage === 5 && data.status === 'complete') {
          router.push(`/results/${runId}`)
          return
        }

        // Continue polling if still running
        if (data.status === 'running') {
          timeoutId = setTimeout(pollStatus, 5000)
        }
      } catch (err) {
        console.error('Polling error:', err)

        // Retry once on network error
        if (retryCount < 1) {
          retryCount++
          timeoutId = setTimeout(pollStatus, 5000)
        } else {
          setError('Network error - unable to connect to server')
          setStatus('error')
          setLoading(false)
        }
      }
    }

    pollStatus()

    // Cleanup function to clear timeout on unmount
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [runId, router])

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Back to Upload
          </button>
        </div>
      </div>
    )
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pipeline status...</p>
        </div>
      </div>
    )
  }


  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Pipeline Execution</h1>
          <p className="text-gray-600">Run ID: {runId}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Stage Boxes */}
          <div className="lg:col-span-1">
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

          {/* Right Column: Track Cards & Detail Panel */}
          <div className="lg:col-span-2">
            {/* Stage 1 Track Cards */}
            {currentStage >= 1 && (
              <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4">Selected Inspiration Tracks</h2>
                {stage1Data ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <PipelineTrackCard
                      trackNumber={1}
                      title={stage1Data.track_1.title}
                      summary={stage1Data.track_1.summary}
                    />
                    <PipelineTrackCard
                      trackNumber={2}
                      title={stage1Data.track_2.title}
                      summary={stage1Data.track_2.summary}
                    />
                  </div>
                ) : currentStage === 1 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Skeleton className="h-40" />
                    <Skeleton className="h-40" />
                  </div>
                ) : null}
              </div>
            )}

            {/* Current Stage Detail Panel */}
            <DetailPanel
              currentStage={currentStage}
              status={status}
              runId={runId}
              brandName={brandName}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

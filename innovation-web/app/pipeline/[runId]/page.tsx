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
  status: 'running' | 'completed' | 'error'
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

  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
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
    const MAX_RETRIES = 3

    // Exponential backoff: 5s, 10s, 20s
    const getRetryDelay = (attempt: number): number => {
      return 5000 * Math.pow(2, attempt) // 5s, 10s, 20s
    }

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
        if (data.current_stage === 5 && data.status === 'completed') {
          router.push(`/results/${runId}`)
          return
        }

        // Continue polling if still running
        if (data.status === 'running') {
          timeoutId = setTimeout(pollStatus, 5000)
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
          setError('Network error - unable to connect to server after multiple retries')
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
      <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center border border-gray-200">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-[#5B9A99] hover:bg-[#4A8887] text-white px-6 py-2.5 rounded-lg transition-colors duration-200 font-medium"
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
      <div className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-teal-100 border-t-[#5B9A99] mx-auto mb-4"></div>
          <p className="text-gray-600 font-medium">Loading pipeline status...</p>
        </div>
      </div>
    )
  }


  // Get selected and non-selected tracks
  const selectedTrack = stage1Data ? (stage1Data.selected_track === 1 ? stage1Data.track_1 : stage1Data.track_2) : null
  const nonSelectedTrack = stage1Data ? (stage1Data.selected_track === 1 ? stage1Data.track_2 : stage1Data.track_1) : null
  const selectedTrackNumber = stage1Data?.selected_track
  const nonSelectedTrackNumber = stage1Data ? (stage1Data.selected_track === 1 ? 2 : 1) : null

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Header with Back button and Company name */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4 max-w-7xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                onClick={() => router.push('/upload')}
                className="flex items-center gap-2 hover:border-[#5B9A99] hover:text-[#5B9A99] transition-colors"
                data-testid="back-button"
              >
                ← Back
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Pipeline Execution</h1>
            </div>
            {brandName && (
              <Badge variant="secondary" className="text-sm bg-teal-50 text-[#5B9A99] border-teal-200" data-testid="company-badge">
                {brandName}
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 md:px-6 py-8 md:py-12 max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8 lg:gap-12">
          {/* Left Sidebar: Stage Boxes + Non-selected Track */}
          <div className="lg:col-span-3 flex-shrink-0 space-y-4 md:space-y-6">
            {/* Stage Boxes - Scrollable Container */}
            <div className="bg-white rounded-xl shadow-md p-4 md:p-6 max-h-[600px] md:max-h-[700px] overflow-y-auto scrollbar-thin scrollbar-thumb-teal-200 scrollbar-track-gray-100">
              <h2 className="text-base md:text-lg font-semibold mb-4 md:mb-6 text-gray-900">Pipeline Stages</h2>
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
                        <div className="text-[#5B9A99] text-xl opacity-30">↓</div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Ideation Tracks - Non-selected track (Fixed size) */}
            {currentStage >= 1 && nonSelectedTrack && nonSelectedTrackNumber && (
              <div className="flex-shrink-0">
                <h3 className="text-sm font-semibold text-gray-600 mb-3 px-1">Ideation Tracks</h3>
                <IdeationTracksSidebar
                  trackNumber={nonSelectedTrackNumber}
                  title={nonSelectedTrack.title}
                  summary={nonSelectedTrack.summary}
                />
              </div>
            )}
          </div>

          {/* Main Content: Selected Track & Detail Panel */}
          <div className="lg:col-span-9">
            {/* Selected Track Card (only one, main content area) */}
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

            {/* Current Stage Detail Panel */}
            <DetailPanel
              currentStage={currentStage}
              status={status === 'completed' ? 'complete' : status}
              runId={runId}
              brandName={brandName}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

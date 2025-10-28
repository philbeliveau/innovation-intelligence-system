'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import PipelineStateMachine from '@/components/pipeline/PipelineStateMachine'

interface PipelineStatus {
  run_id: string
  status: 'running' | 'completed' | 'error'
  current_stage: number
  stages?: Record<string, {
    status: string
    output: string
    completed_at?: string
  }>
  brand_name?: string
}

export default function PipelinePage() {
  const params = useParams()
  const router = useRouter()
  const runId = params.runId as string

  console.log('🔥🔥🔥 NEW PIPELINE PAGE LOADED - OLD UI REMOVED 🔥🔥🔥', { runId })

  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
  const [currentStage, setCurrentStage] = useState<number>(0)
  const [brandName, setBrandName] = useState<string>()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pipelineStages, setPipelineStages] = useState<Array<{
    stageNumber: number
    status: 'pending' | 'processing' | 'completed' | 'failed'
    output?: string
    completedAt?: string
  }>>([])
  const [opportunityCards, setOpportunityCards] = useState<Array<{
    id: string
    number: number
    title: string
    summary: string
    content?: string
    markdown?: string
    createdAt?: string
  }>>([])


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

        const response = await fetch(`/api/pipeline/${runId}/status`)

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

        // Convert stages object to array for PipelineStateMachine
        if (data.stages) {
          const stagesArray = Object.entries(data.stages).map(([stageNum, stageData]) => ({
            stageNumber: parseInt(stageNum),
            status: stageData.status as 'pending' | 'processing' | 'completed' | 'failed',
            output: stageData.output,
            completedAt: stageData.completed_at,
          }))
          setPipelineStages(stagesArray)
        }

        // Fetch opportunity cards if pipeline is completed
        if (data.status === 'completed') {
          try {
            const cardsResponse = await fetch(`/api/pipeline/${runId}/opportunity-cards`)
            if (cardsResponse.ok) {
              const cardsData = await cardsResponse.json()
              setOpportunityCards(cardsData.opportunityCards || [])
            }
          } catch (e) {
            console.error('Failed to fetch opportunity cards:', e)
          }
        }

        setBrandName(data.brand_name)
        setLoading(false)
        retryCount = 0 // Reset retry count on success

        console.log(`[Pipeline] Status: ${data.status}, Stage: ${data.current_stage}`)

        if (data.status === 'error') {
          setError('Pipeline failed')
          return
        }

        // Continue polling if still running
        if (data.status === 'running') {
          timeoutId = setTimeout(pollStatus, 5000)
        }

        // Note: We don't auto-redirect anymore - let user click the button
        // This prevents issues with router.push on mobile and gives user control
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

  return (
    <div className="min-h-screen bg-[#F5F5F5]">
      {/* Header with Back button and Company name - Mobile responsive */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-3 sm:py-4 max-w-7xl">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div className="flex items-center gap-2 sm:gap-4">
              <Button
                variant="outline"
                onClick={() => router.push('/upload')}
                className="flex items-center gap-1 sm:gap-2 hover:border-[#5B9A99] hover:text-[#5B9A99] transition-colors text-xs sm:text-sm px-2 sm:px-4"
                data-testid="back-button"
              >
                ← Back
              </Button>
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold text-gray-900">Pipeline Execution</h1>
            </div>
            {brandName && (
              <Badge variant="secondary" className="text-xs sm:text-sm bg-teal-50 text-[#5B9A99] border-teal-200" data-testid="company-badge">
                {brandName}
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Main Content: PipelineStateMachine (Epic 8) */}
      <div className="container mx-auto px-4 md:px-6 py-4 sm:py-8 md:py-12 max-w-7xl">
        <PipelineStateMachine
          currentStage={currentStage}
          status={status === 'completed' ? 'COMPLETED' : status === 'running' ? 'PROCESSING' : 'FAILED'}
          pipelineData={{
            runId,
            stages: pipelineStages,
            opportunityCards,
            brandName,
          }}
        />
      </div>
    </div>
  )
}

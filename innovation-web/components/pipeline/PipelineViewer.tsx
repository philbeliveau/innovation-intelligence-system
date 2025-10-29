'use client'

import { useEffect, useState } from 'react'
import PipelineStateMachine from './PipelineStateMachine'
import CoffeeMachineLoader from '../CoffeeMachineLoader'

interface PipelineStatus {
  run_id: string
  status: 'running' | 'processing' | 'complete' | 'completed' | 'error'
  current_stage: number
  stages?: Record<string, {
    status: string
    output: string
    completed_at?: string
  }>
  brand_name?: string
}

interface PipelineViewerProps {
  runId: string
  onComplete?: (runId: string) => void
  onError?: (error: string) => void
  inlineMode?: boolean
  onSignalCardClick?: () => void
}

export default function PipelineViewer({
  runId,
  onComplete,
  onError,
  inlineMode = false,
  onSignalCardClick
}: PipelineViewerProps) {
  const [status, setStatus] = useState<'running' | 'completed' | 'error'>('running')
  const [currentStage, setCurrentStage] = useState<number>(0)
  const [brandName, setBrandName] = useState<string>()
  const [loading, setLoading] = useState(true)
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

  console.log('🔥🔥🔥 NEW PIPELINEVIEWER WITH STATE MACHINE 🔥🔥🔥', { runId, inlineMode })

  // Validate run ID format before starting
  useEffect(() => {
    if (!runId || runId.trim() === '') {
      const errorMsg = 'Invalid run ID provided'
      console.error('[PipelineViewer] ERROR: Invalid run ID:', runId)
      setStatus('error')
      setLoading(false)
      onError?.(errorMsg)
      return
    }
  }, [runId, onError])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout | undefined
    let retryCount = 0
    let isFirstPoll = true
    let isCancelled = false
    const startTime = Date.now()
    const MAX_RUNTIME = 35 * 60 * 1000
    const MAX_RETRIES = 3

    const getRetryDelay = (attempt: number): number => {
      return 5000 * Math.pow(2, attempt)
    }

    const pollStatus = async () => {
      if (isCancelled) return

      try {
        // Add 2-second delay before first poll
        if (isFirstPoll) {
          isFirstPoll = false
          await new Promise(resolve => setTimeout(resolve, 2000))
        }

        // Check for timeout
        const elapsed = Date.now() - startTime
        if (elapsed > MAX_RUNTIME) {
          const errorMsg = 'Pipeline timeout - exceeded 35 minutes'
          setStatus('error')
          setLoading(false)
          onError?.(errorMsg)
          return
        }

        const statusUrl = `/api/pipeline/${runId}/status`
        const response = await fetch(statusUrl)

        // Treat initial 404s as "pipeline starting up"
        if (response.status === 404) {
          if (retryCount < 5) {
            retryCount++
            console.log(`[PipelineViewer] Pipeline starting... retry ${retryCount}/5`)
            timeoutId = setTimeout(pollStatus, 1000)
            return
          } else {
            const errorMsg = `Pipeline run not found. Run ID: ${runId}. Please try launching again.`
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

        // Normalize status
        let normalizedStatus: 'running' | 'completed' | 'error' = 'running'
        if (data.status === 'complete' || data.status === 'completed') {
          normalizedStatus = 'completed'
        } else if (data.status === 'error') {
          normalizedStatus = 'error'
        } else {
          normalizedStatus = 'running'
        }

        setStatus(normalizedStatus)
        setCurrentStage(data.current_stage)
        setBrandName(data.brand_name)

        // Convert stages object to array for PipelineStateMachine
        if (data.stages) {
          const stagesArray = Object.entries(data.stages).map(([stageNum, stageData]) => ({
            stageNumber: parseInt(stageNum),
            status: stageData.status as 'pending' | 'processing' | 'completed' | 'failed',
            output: stageData.output,
            completedAt: stageData.completed_at,
          }))
          setPipelineStages(stagesArray)

          // Extract opportunities from Stage 5 output as soon as available
          const stage5Data = data.stages['5']
          if (stage5Data?.output) {
            try {
              // Parse Stage 5 output (handle both string and object)
              const stage5Output = typeof stage5Data.output === 'string'
                ? JSON.parse(stage5Data.output)
                : stage5Data.output

              // Extract opportunities array if present
              if (stage5Output?.opportunities && Array.isArray(stage5Output.opportunities)) {
                const cards = stage5Output.opportunities.map((opp: { number?: number; title?: string; description?: string; markdown?: string; content?: string }, idx: number) => ({
                  id: `stage5-${opp.number || idx + 1}`,
                  number: opp.number || idx + 1,
                  title: opp.title || `Spark ${idx + 1}`,
                  summary: (opp.description || opp.markdown || '').substring(0, 200),
                  content: opp.markdown || opp.description || opp.content || '',
                  markdown: opp.markdown,
                }))
                setOpportunityCards(cards)
                console.log(`[PipelineViewer] Extracted ${cards.length} opportunities from Stage 5 output`)
              }
            } catch (parseError) {
              console.warn('[PipelineViewer] Failed to parse Stage 5 output:', parseError)
            }
          }
        }

        // Fetch opportunity cards from database if pipeline is completed (for persistent IDs)
        if (normalizedStatus === 'completed') {
          try {
            const cardsResponse = await fetch(`/api/pipeline/${runId}/opportunity-cards`)
            if (cardsResponse.ok) {
              const cardsData = await cardsResponse.json()
              if (cardsData.opportunityCards && cardsData.opportunityCards.length > 0) {
                setOpportunityCards(cardsData.opportunityCards)
                console.log(`[PipelineViewer] Fetched ${cardsData.opportunityCards.length} opportunity cards from database`)
              }
            }
          } catch (e) {
            console.error('Failed to fetch opportunity cards from database:', e)
          }
        }

        setLoading(false)
        retryCount = 0

        if (data.status === 'error') {
          onError?.('Pipeline failed')
          return
        }

        // Handle completion
        if (data.current_stage === 5 && (data.status === 'complete' || data.status === 'completed')) {
          console.log('[PipelineViewer] Pipeline completed!')
          onComplete?.(runId)
          return
        }

        // Continue polling if still running
        if (data.status === 'running' || data.status === 'processing') {
          timeoutId = setTimeout(pollStatus, 5000)
        }
      } catch (err) {
        console.error('Polling error:', err)

        if (retryCount < MAX_RETRIES) {
          const delay = getRetryDelay(retryCount)
          retryCount++
          timeoutId = setTimeout(pollStatus, delay)
        } else {
          const errorMsg = 'Network error - unable to connect to server'
          setStatus('error')
          setLoading(false)
          onError?.(errorMsg)
        }
      }
    }

    pollStatus()

    return () => {
      isCancelled = true
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
    }
  }, [runId, onComplete, onError])

  // Loading state
  if (loading) {
    return (
      <div className={inlineMode ? 'space-y-4' : 'min-h-screen bg-[#F5F5F5] flex items-center justify-center'}>
        <CoffeeMachineLoader />
      </div>
    )
  }

  return (
    <div className={inlineMode ? '' : ''}>
      <PipelineStateMachine
        currentStage={currentStage}
        status={status === 'completed' ? 'COMPLETED' : status === 'running' ? 'PROCESSING' : 'FAILED'}
        pipelineData={{
          runId,
          stages: pipelineStages,
          opportunityCards,
          brandName,
        }}
        onSignalCardClick={onSignalCardClick}
      />
    </div>
  )
}

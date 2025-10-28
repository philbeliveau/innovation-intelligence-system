'use client'

import { useState, useEffect } from 'react'
import {
  PipelineState,
  PipelineStateMachineProps,
  PipelineStatus,
} from '@/types/pipeline-state'
import ExtractionAnimation from './ExtractionAnimation'
import WorkflowIllustration from './WorkflowIllustration'
import { ThreeColumnLayout } from './ThreeColumnLayout'
import { SignalsColumn } from './SignalsColumn'
import { TransferableInsightsColumn } from './TransferableInsightsColumn'
import { SparksPreviewColumn } from './SparksPreviewColumn'
import {
  SignalsColumnSkeleton,
  TransferableInsightsColumnSkeleton,
  SparksPreviewColumnSkeleton,
} from './LoadingSkeletons'
import IconNavigation from './IconNavigation'
import SparksGrid from './SparksGrid'
import ActionBar from './ActionBar'
import CollapsedSidebar from './CollapsedSidebar'
import ExpandedSparkDetail from './ExpandedSparkDetail'
import { useRouter } from 'next/navigation'
import { FadeTransition } from '../animations/FadeTransition'
import { StateAnnouncer } from '../animations/StateAnnouncer'

/**
 * Helper to safely parse stage output JSON
 */
const parseStageOutput = (output: string | undefined) => {
  if (!output) return null
  try {
    return JSON.parse(output)
  } catch {
    return null
  }
}

/**
 * Determines current UI state based on pipeline progress
 */
const determineCurrentState = (
  currentStage: number,
  status: PipelineStatus,
  selectedCardId: string | null | undefined
): PipelineState => {
  if (status === 'COMPLETED' && selectedCardId !== null && selectedCardId !== undefined) {
    return PipelineState.State4 // Detail view
  }
  if (status === 'COMPLETED') {
    return PipelineState.State3 // Grid view
  }
  if (currentStage >= 2 && status === 'PROCESSING') {
    return PipelineState.State2 // 3-column progress
  }
  return PipelineState.State1 // Extraction animation
}

export default function PipelineStateMachine({
  currentStage,
  status,
  pipelineData,
  selectedCardId,
  onCardSelect,
}: PipelineStateMachineProps) {
  const router = useRouter()
  const [internalSelectedCardId, setInternalSelectedCardId] = useState<string | null>(null)
  const [isDownloading, setIsDownloading] = useState(false)
  const [previousState, setPreviousState] = useState<PipelineState | null>(null)
  const [announceMessage, setAnnounceMessage] = useState('')

  // Use controlled or uncontrolled card selection
  const activeCardId = selectedCardId !== undefined ? selectedCardId : internalSelectedCardId
  const handleCardSelect = (cardId: string) => {
    if (onCardSelect) {
      onCardSelect(cardId)
    } else {
      setInternalSelectedCardId(cardId)
    }
  }

  // Download all sparks handler
  const handleDownloadAll = async () => {
    setIsDownloading(true)
    try {
      const response = await fetch(`/api/pipeline/${pipelineData.runId}/download/all`)
      if (!response.ok) {
        throw new Error('Download failed')
      }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `sparks-${pipelineData.runId}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Download error:', error)
      alert('Failed to download sparks. Please try again.')
    } finally {
      setIsDownloading(false)
    }
  }

  // New pipeline handler
  const handleNewPipeline = () => {
    router.push('/upload')
  }

  const currentState = determineCurrentState(currentStage, status, activeCardId)

  // Announce state changes for accessibility
  useEffect(() => {
    if (previousState !== null && previousState !== currentState) {
      const messages = {
        [PipelineState.State1]: 'Extracting trend data from document',
        [PipelineState.State2]: 'Processing insights and generating sparks',
        [PipelineState.State3]: `Pipeline complete. Displaying ${pipelineData.opportunityCards?.length || 0} sparks.`,
        [PipelineState.State4]: 'Viewing spark detail',
      }
      setAnnounceMessage(messages[currentState] || '')
    }
    setPreviousState(currentState)
  }, [currentState, previousState, pipelineData.opportunityCards?.length])

  // Keyboard navigation for State 4
  useEffect(() => {
    if (currentState !== PipelineState.State4 || !activeCardId || !pipelineData.opportunityCards) {
      return
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      const currentIndex = pipelineData.opportunityCards!.findIndex(
        (card) => card.id === activeCardId
      )

      if (e.key === 'ArrowDown' && currentIndex < pipelineData.opportunityCards!.length - 1) {
        e.preventDefault()
        handleCardSelect(pipelineData.opportunityCards![currentIndex + 1].id)
      } else if (e.key === 'ArrowUp' && currentIndex > 0) {
        e.preventDefault()
        handleCardSelect(pipelineData.opportunityCards![currentIndex - 1].id)
      } else if (e.key === 'Escape') {
        e.preventDefault()
        handleCardSelect('')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentState, activeCardId, pipelineData.opportunityCards])

  return (
    <>
      {/* Screen reader announcements */}
      {announceMessage && <StateAnnouncer message={announceMessage} />}

      <div className="relative">
        {/* State 1: Extraction Animation */}
        <FadeTransition isVisible={currentState === PipelineState.State1}>
          <div
            className="grid grid-cols-1 lg:grid-cols-2 gap-6"
            data-testid="state-1"
          >
            {/* Left Box: Extraction Animation */}
            <div className="relative bg-white rounded-lg shadow-md p-8 min-h-[400px]">
              <ExtractionAnimation status={status === 'FAILED' ? 'error' : 'running'} />
            </div>

            {/* Right Box: Workflow Illustration */}
            <div className="relative bg-white rounded-lg shadow-md p-8 min-h-[400px]">
              <WorkflowIllustration />
            </div>
          </div>
        </FadeTransition>

        {/* State 2: Three Column Progress */}
        <FadeTransition isVisible={currentState === PipelineState.State2}>
          <div data-testid="state-2">
          {(() => {
            // Parse stage outputs - handle both JSON object and string formats
            const stage1Output = pipelineData.stages.find((s) => s.stageNumber === 1)?.output
            const stage1Data = typeof stage1Output === 'string' ? parseStageOutput(stage1Output) : stage1Output

            // Stage 1 is COMPLETED if we have any data at all
            const hasStage1Data = stage1Data && Object.keys(stage1Data).length > 0

            // Extract data for columns with fallbacks for missing structured data
            const trendTitle = stage1Data?.trend_title || stage1Data?.inspiration_1_title || 'Analyzing Document Signal...'
            const trendImage = stage1Data?.trend_image || undefined
            const coreMechanism = stage1Data?.core_mechanism || stage1Data?.inspiration_1_content?.substring(0, 200) || 'Extracting transferable patterns...'
            const businessImpact = stage1Data?.business_impact || 'Analyzing brand relevance...'
            const patternTransfersTo = stage1Data?.pattern_transfers_to || []

            // Convert opportunity cards to spark previews
            const sparks =
              pipelineData.opportunityCards?.map((card) => ({
                number: card.number,
                title: card.title,
                summary: card.summary,
                heroImageUrl: undefined, // TODO: Add hero image to opportunity cards
              })) || []

            return (
              <ThreeColumnLayout>
                {hasStage1Data ? (
                  <SignalsColumn trendImage={trendImage} trendTitle={trendTitle} />
                ) : (
                  <SignalsColumnSkeleton />
                )}

                {hasStage1Data ? (
                  <TransferableInsightsColumn
                    coreMechanism={coreMechanism}
                    businessImpact={businessImpact}
                    patternTransfersTo={patternTransfersTo}
                    runId={pipelineData.runId}
                    onDownload={() => {
                      // Download handler will be implemented in next task
                      window.open(`/api/pipeline/${pipelineData.runId}/download/stage1`, '_blank')
                    }}
                  />
                ) : (
                  <TransferableInsightsColumnSkeleton />
                )}

                {sparks.length > 0 ? (
                  <SparksPreviewColumn sparks={sparks} isGenerating={currentStage < 5} />
                ) : (
                  <SparksPreviewColumnSkeleton />
                )}
              </ThreeColumnLayout>
            )
          })()}
          </div>
        </FadeTransition>

        {/* State 3: Sparks Grid with Slide-Up Animation */}
        <FadeTransition isVisible={currentState === PipelineState.State3}>
          <div data-testid="state-3">
          {/* State 3: All Complete - Sparks Grid View */}
          <IconNavigation activeSection="sparks" />
          <SparksGrid
            sparks={
              pipelineData.opportunityCards?.map((card) => ({
                id: card.id,
                title: card.title,
                summary: card.summary || '',
                heroImageUrl: undefined, // TODO: Add hero images
                content: card.content || card.markdown || '',
              })) || []
            }
            onCardClick={handleCardSelect}
          />
          <ActionBar
            onDownloadAll={handleDownloadAll}
            onNewPipeline={handleNewPipeline}
            isDownloading={isDownloading}
            sparkCount={pipelineData.opportunityCards?.length || 0}
          />
          </div>
        </FadeTransition>

        {/* State 4: Detail View with Sidebar Collapse Animation */}
        {currentState === PipelineState.State4 && activeCardId && (
          <div
            className="flex flex-row h-full"
            data-testid="state-4"
          >
            {/* State 4: Collapsed Sidebar + Expanded Detail View */}
            <div className="hidden md:block">
              <CollapsedSidebar
                sparks={
                  pipelineData.opportunityCards?.map((card) => ({
                    id: card.id,
                    title: card.title,
                    summary: card.summary || '',
                    heroImageUrl: undefined, // TODO: Add hero images
                    content: card.content || card.markdown || '',
                  })) || []
                }
                selectedId={activeCardId}
                onSelectSpark={handleCardSelect}
                isCollapsed={true}
              />
            </div>

          {(() => {
            const selectedCard = pipelineData.opportunityCards?.find(
              (card) => card.id === activeCardId
            )
            const currentIndex = pipelineData.opportunityCards?.findIndex(
              (card) => card.id === activeCardId
            ) || 0
            const totalSparks = pipelineData.opportunityCards?.length || 0

            if (!selectedCard) return null

            return (
              <ExpandedSparkDetail
                spark={{
                  id: selectedCard.id,
                  title: selectedCard.title,
                  summary: selectedCard.summary || '',
                  heroImageUrl: undefined, // TODO: Add hero images
                  content: selectedCard.content || selectedCard.markdown || '',
                }}
                onBack={() => handleCardSelect('')}
                currentIndex={currentIndex}
                totalSparks={totalSparks}
                onPrev={() => {
                  if (currentIndex > 0 && pipelineData.opportunityCards) {
                    handleCardSelect(pipelineData.opportunityCards[currentIndex - 1].id)
                  }
                }}
                onNext={() => {
                  if (
                    currentIndex < totalSparks - 1 &&
                    pipelineData.opportunityCards
                  ) {
                    handleCardSelect(pipelineData.opportunityCards[currentIndex + 1].id)
                  }
                }}
              />
            )
          })()}
          </div>
        )}
      </div>
    </>
  )
}

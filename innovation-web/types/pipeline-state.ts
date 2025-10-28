/**
 * TypeScript interfaces for Pipeline State Machine
 * Defines types for all 4 progressive UI states
 */

export enum PipelineState {
  State1 = 'STATE_1', // Stage 1 running - Extraction animation
  State2 = 'STATE_2', // Stages 2-5 running - 3-column layout
  State3 = 'STATE_3', // All complete - Sparks grid view
  State4 = 'STATE_4', // Card detail view - Expanded spark
}

export type PipelineStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'

export interface OpportunityCardData {
  id: string
  number: number
  title: string
  summary: string
  markdown?: string
  content?: string
  createdAt?: string
}

export interface StageData {
  stageNumber: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  output?: string
  completedAt?: string
}

export interface PipelineData {
  runId: string
  stages: StageData[]
  opportunityCards?: OpportunityCardData[]
  brandName?: string
}

export interface PipelineStateMachineProps {
  currentStage: number
  status: PipelineStatus
  pipelineData: PipelineData
  selectedCardId?: string | null
  onCardSelect?: (cardId: string) => void
  onSignalCardClick?: () => void
}

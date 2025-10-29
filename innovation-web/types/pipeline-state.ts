/**
 * TypeScript interfaces for Pipeline State Machine
 * Defines types for all 4 progressive UI states
 *
 * Story 10.5: Added stage output types for retrospective mode
 */

export enum PipelineState {
  State1 = 'STATE_1', // Stage 1 running - Extraction animation
  State2 = 'STATE_2', // Stages 2-5 running - 3-column layout
  State3 = 'STATE_3', // All complete - Sparks grid view
  State4 = 'STATE_4', // Card detail view - Expanded spark
}

export type PipelineStatus = 'PROCESSING' | 'COMPLETED' | 'FAILED' | 'CANCELLED'

// Story 10.5: Stage output type definitions for retrospective mode
export type Stage1Output = {
  extractedText: string
  mechanisms: Array<{
    title: string
    description: string
    categoryTags: string[]
  }>
}

export type Stage2Output = {
  signals: Array<{
    title: string
    amplifiedInsight: string
    strengthFactors: string[]
  }>
}

export type Stage3Output = {
  insights: Array<{
    title: string
    generalizedInsight: string
    applicationDomains: string[]
  }>
}

export type Stage4Output = {
  preliminary: Array<{
    title: string
    contextualizedIdea: string
    relevanceToPortfolio: string
  }>
}

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
  // Story 10.5: Added stage output fields for retrospective mode
  stage1Output?: Stage1Output | null
  stage2Output?: Stage2Output | null
  stage3Output?: Stage3Output | null
  stage4Output?: Stage4Output | null
  hasFullReport?: boolean
}

export interface PipelineStateMachineProps {
  currentStage: number
  status: PipelineStatus
  pipelineData: PipelineData
  selectedCardId?: string | null
  onCardSelect?: (cardId: string) => void
  onSignalCardClick?: () => void
}

// Story 10.5: API response type for status endpoint
export interface PipelineStatusResponse {
  run_id: string
  status: string  // Lowercase version: 'processing' | 'completed' | 'failed'
  current_stage: number
  stages: Record<string, {
    status: string
    output?: unknown
    completed_at?: string | null
  }>
  brand_name?: string
  partialOpportunities?: Array<{
    id: string
    number: number
    title: string
    summary: string
    heroImageUrl: string | null
    isComplete: boolean
  }>
  // NEW FIELDS (Story 10.5) - Retrospective mode support
  stage1Output?: Stage1Output | null
  stage2Output?: Stage2Output | null
  stage3Output?: Stage3Output | null
  stage4Output?: Stage4Output | null
  hasFullReport: boolean
}

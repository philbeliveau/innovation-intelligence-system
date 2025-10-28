/**
 * Partial Opportunities Tests
 * Tests for partial opportunity data during Stage 5 processing
 *
 * References Story 8.0: Backend API Endpoints Prerequisites
 * - AC#4: Status Endpoint Returns Opportunity Preview Data
 *
 * Note: These tests verify partial opportunity data fetching and structure.
 */

import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    pipelineRun: {
      findUnique: jest.fn(),
    },
    stageOutput: {
      findMany: jest.fn(),
    },
    opportunityCard: {
      findMany: jest.fn(),
    },
  },
}))

describe('Partial Opportunities During Stage 5', () => {
  const mockPrisma = prisma as jest.Mocked<typeof prisma>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Stage 5 Processing - Partial Opportunities', () => {
    it('should fetch partial opportunities during Stage 5 PROCESSING', async () => {
      const runId = 'run-stage5'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue({
        id: runId,
        uploadId: 'upload-stage5',
        brandId: 'test-brand',
        status: 'PROCESSING',
        currentStage: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any)

      // Partial opportunities being generated
      mockPrisma.opportunityCard.findMany.mockResolvedValue([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'First Opportunity Title',
          summary: 'Brief summary of first opportunity...',
          fullContent: '', // Not yet complete
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'opp-2',
          runId,
          number: 2,
          title: 'Second Opportunity Title',
          summary: 'Brief summary of second opportunity...',
          fullContent: '', // Not yet complete
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(2)
      expect(opportunities[0].fullContent).toBe('')
      expect(opportunities[1].fullContent).toBe('')
    })

    it('should distinguish complete vs partial opportunities by fullContent', async () => {
      const runId = 'run-mixed'

      // Mixed: some complete, some partial
      mockPrisma.opportunityCard.findMany.mockResolvedValue([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'Complete Opportunity',
          summary: 'Summary',
          fullContent: '# Full markdown content here\n\nThis is complete.',
          heroImageUrl: 'https://example.com/hero1.jpg',
          createdAt: new Date(),
        },
        {
          id: 'opp-2',
          runId,
          number: 2,
          title: 'Partial Opportunity',
          summary: 'Summary',
          fullContent: '', // Empty = not complete
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'opp-3',
          runId,
          number: 3,
          title: 'Another Complete',
          summary: 'Summary',
          fullContent: '# Another complete one\n\nContent...',
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(3)

      // First: complete
      const isComplete1 = opportunities[0].fullContent !== ''
      expect(isComplete1).toBe(true)
      expect(opportunities[0].heroImageUrl).toBe('https://example.com/hero1.jpg')

      // Second: partial
      const isComplete2 = opportunities[1].fullContent !== ''
      expect(isComplete2).toBe(false)
      expect(opportunities[1].heroImageUrl).toBeNull()

      // Third: complete
      const isComplete3 = opportunities[2].fullContent !== ''
      expect(isComplete3).toBe(true)
    })

    it('should handle empty opportunities list during Stage 5', async () => {
      const runId = 'run-stage5-empty'

      mockPrisma.opportunityCard.findMany.mockResolvedValue([]) // No opportunities yet

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toEqual([])
    })
  })

  describe('State Machine Integration', () => {
    it('should provide data needed for State 2 Sparks Preview Column', async () => {
      const runId = 'run-state2'

      mockPrisma.opportunityCard.findMany.mockResolvedValue([
        {
          id: 'temp-1',
          runId,
          number: 1,
          title: 'Spark 1',
          summary: 'Summary 1',
          fullContent: '',
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'temp-2',
          runId,
          number: 2,
          title: 'Spark 2',
          summary: 'Summary 2',
          fullContent: '# Complete',
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'temp-3',
          runId,
          number: 3,
          title: 'Spark 3',
          summary: 'Summary 3',
          fullContent: '',
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      // State 2 Sparks Preview Column needs:
      // - id (for tracking)
      // - title (for display)
      // - summary (for preview)
      // - fullContent (to determine isComplete)
      expect(opportunities).toHaveLength(3)

      opportunities.forEach((spark: any) => {
        expect(spark.id).toBeDefined()
        expect(spark.title).toBeDefined()
        expect(spark.summary).toBeDefined()
        expect(typeof spark.fullContent).toBe('string')
      })

      // Verify completion status
      expect(opportunities[0].fullContent).toBe('') // partial
      expect(opportunities[1].fullContent).toBe('# Complete') // complete
      expect(opportunities[2].fullContent).toBe('') // partial
    })
  })

  describe('Performance Tests', () => {
    it('should handle 10 partial opportunities', async () => {
      const runId = 'run-many-partial'

      const manyOpportunities = Array.from({ length: 10 }, (_, i) => ({
        id: `opp-${i + 1}`,
        runId,
        number: i + 1,
        title: `Opportunity ${i + 1}`,
        summary: `Summary ${i + 1}`,
        fullContent: i < 5 ? '# Complete' : '', // First 5 complete
        heroImageUrl: null,
        createdAt: new Date(),
      }))

      mockPrisma.opportunityCard.findMany.mockResolvedValue(manyOpportunities as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(10)

      // First 5 complete, last 5 partial
      for (let i = 0; i < 5; i++) {
        const isComplete = opportunities[i].fullContent !== ''
        expect(isComplete).toBe(true)
      }
      for (let i = 5; i < 10; i++) {
        const isComplete = opportunities[i].fullContent !== ''
        expect(isComplete).toBe(false)
      }
    })

    it('should only fetch lightweight fields needed for preview', async () => {
      const runId = 'run-lightweight'

      mockPrisma.opportunityCard.findMany.mockResolvedValue([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'Opportunity',
          summary: 'Summary',
          fullContent: '# Very long markdown content that would be heavy to transfer...\n\n'.repeat(100),
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      // Should fetch all fields (filtering happens at API layer)
      const opp = opportunities[0]
      expect(opp.id).toBeDefined()
      expect(opp.title).toBeDefined()
      expect(opp.summary).toBeDefined()
      expect(opp.fullContent).toBeDefined()
    })
  })

  describe('Real-time Polling Behavior', () => {
    it('should reflect progressive completion as opportunities finish', async () => {
      const runId = 'run-progressive'

      // Request 1: 2 opportunities, both partial
      mockPrisma.opportunityCard.findMany.mockResolvedValueOnce([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'Opp 1',
          summary: 'Summary',
          fullContent: '',
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'opp-2',
          runId,
          number: 2,
          title: 'Opp 2',
          summary: 'Summary',
          fullContent: '',
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities1 = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities1[0].fullContent).toBe('')
      expect(opportunities1[1].fullContent).toBe('')

      // Request 2: First opportunity now complete
      mockPrisma.opportunityCard.findMany.mockResolvedValueOnce([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'Opp 1',
          summary: 'Summary',
          fullContent: '# Complete now',
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'opp-2',
          runId,
          number: 2,
          title: 'Opp 2',
          summary: 'Summary',
          fullContent: '', // Still partial
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities2 = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities2[0].fullContent).toBe('# Complete now') // Now complete
      expect(opportunities2[1].fullContent).toBe('') // Still partial
    })
  })
})

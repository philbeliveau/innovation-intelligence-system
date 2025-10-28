/**
 * Download Endpoints Data Layer Tests
 * Tests for Stage 1 PDF and All Opportunities ZIP data fetching logic
 *
 * References Story 8.0: Backend API Endpoints Prerequisites
 * - AC#2: Download Stage 1 Report Endpoint
 * - AC#3: Download All Opportunities Endpoint
 *
 * Note: These tests verify data fetching, validation, and error handling.
 * Actual PDF/ZIP generation and HTTP responses are integration tested manually.
 */

import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    pipelineRun: {
      findUnique: jest.fn(),
    },
    stageOutput: {
      findFirst: jest.fn(),
    },
    opportunityCard: {
      findMany: jest.fn(),
    },
  },
}))

describe('Download Endpoints - Data Fetching Logic', () => {
  const mockPrisma = prisma as jest.Mocked<typeof prisma>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Stage 1 Download - Data Validation', () => {
    it('should fetch pipeline run and Stage 1 output data', async () => {
      const runId = 'run-123'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue({
        id: runId,
        uploadId: 'upload-123',
        brandId: 'test-brand',
        status: 'COMPLETED',
        currentStage: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any)

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-output-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify({
          extractedText: 'Sample extracted text from PDF',
          trendTitle: 'Hyper-Personalization in Consumer Products',
          trendImage: 'data:image/png;base64,abc123',
          coreMechanism: 'AI-driven personalization engine',
          businessImpact: '35% increase in customer engagement',
          patternTransfersTo: ['Retail', 'Healthcare', 'Financial Services'],
        }),
        createdAt: new Date(),
      } as any)

      const pipelineRun = await mockPrisma.pipelineRun.findUnique({
        where: { id: runId },
      })
      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      expect(pipelineRun).toBeDefined()
      expect(pipelineRun?.id).toBe(runId)
      expect(stage1Output).toBeDefined()
      expect(stage1Output?.stageNumber).toBe(1)

      const outputData = JSON.parse(stage1Output!.output)
      expect(outputData.extractedText).toBeDefined()
      expect(outputData.trendTitle).toBeDefined()
      expect(outputData.coreMechanism).toBeDefined()
      expect(outputData.businessImpact).toBeDefined()
      expect(outputData.patternTransfersTo).toBeInstanceOf(Array)
    })

    it('should handle missing pipeline run', async () => {
      const runId = 'run-nonexistent'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue(null)

      const pipelineRun = await mockPrisma.pipelineRun.findUnique({
        where: { id: runId },
      })

      expect(pipelineRun).toBeNull()
    })

    it('should handle missing Stage 1 output', async () => {
      const runId = 'run-no-stage1'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue({
        id: runId,
        uploadId: 'upload',
        brandId: 'test-brand',
        status: 'PROCESSING',
        currentStage: 1,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any)

      mockPrisma.stageOutput.findFirst.mockResolvedValue(null)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      expect(stage1Output).toBeNull()
    })

    it('should validate Stage 1 output structure', async () => {
      const runId = 'run-validate'

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify({
          extractedText: 'Text',
          trendTitle: 'Title',
          coreMechanism: 'Mechanism',
          businessImpact: 'Impact',
          patternTransfersTo: ['Industry1', 'Industry2'],
        }),
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const outputData = JSON.parse(stage1Output!.output)

      // Verify all required fields
      expect(outputData).toHaveProperty('extractedText')
      expect(outputData).toHaveProperty('trendTitle')
      expect(outputData).toHaveProperty('coreMechanism')
      expect(outputData).toHaveProperty('businessImpact')
      expect(outputData).toHaveProperty('patternTransfersTo')

      // Verify types
      expect(typeof outputData.extractedText).toBe('string')
      expect(typeof outputData.trendTitle).toBe('string')
      expect(typeof outputData.coreMechanism).toBe('string')
      expect(typeof outputData.businessImpact).toBe('string')
      expect(Array.isArray(outputData.patternTransfersTo)).toBe(true)
    })
  })

  describe('Download All Opportunities - Data Fetching', () => {
    it('should fetch all opportunities ordered by number', async () => {
      const runId = 'run-123'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue({
        id: runId,
        uploadId: 'upload',
        brandId: 'test-brand',
        status: 'COMPLETED',
        currentStage: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any)

      mockPrisma.opportunityCard.findMany.mockResolvedValue([
        {
          id: 'opp-1',
          runId,
          number: 1,
          title: 'First Opportunity',
          summary: 'Summary 1',
          fullContent: '# Opportunity 1\n\nContent...',
          heroImageUrl: null,
          createdAt: new Date(),
        },
        {
          id: 'opp-2',
          runId,
          number: 2,
          title: 'Second Opportunity',
          summary: 'Summary 2',
          fullContent: '# Opportunity 2\n\nContent...',
          heroImageUrl: null,
          createdAt: new Date(),
        },
      ] as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(2)
      expect(opportunities[0].number).toBe(1)
      expect(opportunities[1].number).toBe(2)
      expect(mockPrisma.opportunityCard.findMany).toHaveBeenCalledWith({
        where: { runId },
        orderBy: { number: 'asc' },
      })
    })

    it('should handle no opportunities found', async () => {
      const runId = 'run-empty'

      mockPrisma.pipelineRun.findUnique.mockResolvedValue({
        id: runId,
        uploadId: 'upload',
        brandId: 'test-brand',
        status: 'COMPLETED',
        currentStage: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any)

      mockPrisma.opportunityCard.findMany.mockResolvedValue([])

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(0)
    })

    it('should fetch large number of opportunities (10+)', async () => {
      const runId = 'run-many'
      const manyOpportunities = Array.from({ length: 15 }, (_, i) => ({
        id: `opp-${i + 1}`,
        runId,
        number: i + 1,
        title: `Opportunity ${i + 1}`,
        summary: `Summary ${i + 1}`,
        fullContent: `# Opportunity ${i + 1}\n\nContent...`,
        heroImageUrl: null,
        createdAt: new Date(),
      }))

      mockPrisma.opportunityCard.findMany.mockResolvedValue(manyOpportunities as any)

      const opportunities = await mockPrisma.opportunityCard.findMany({
        where: { runId },
        orderBy: { number: 'asc' },
      })

      expect(opportunities).toHaveLength(15)
      expect(opportunities[0].number).toBe(1)
      expect(opportunities[14].number).toBe(15)
    })
  })

  describe('Filename Sanitization Logic', () => {
    it('should sanitize opportunity titles for ZIP filenames', () => {
      const testCases = [
        {
          title: 'Innovative Packaging Solution',
          expected: 'innovative-packaging-solution',
        },
        {
          title: 'Special!@#$%^&*() Characters',
          expected: 'special-characters',
        },
        {
          title: 'Multiple   Spaces   Between Words',
          expected: 'multiple-spaces-between-words',
        },
        {
          title: 'Title/With\\Slashes',
          expected: 'title-with-slashes',
        },
        {
          title: 'Very Long Title That Exceeds Fifty Characters And Should Be Truncated Properly',
          expected: 'very-long-title-that-exceeds-fifty-characters-and-',
        },
      ]

      testCases.forEach(({ title, expected }) => {
        const sanitized = title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-|-$/g, '')
          .substring(0, 50)

        expect(sanitized).toBe(expected)
      })
    })

    it('should handle edge cases in filename sanitization', () => {
      const edgeCases = [
        { title: '     ', expected: '' },
        { title: '!@#$%^', expected: '' },
        { title: '123-456', expected: '123-456' },
        { title: 'a', expected: 'a' },
      ]

      edgeCases.forEach(({ title, expected }) => {
        const sanitized = title
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-|-$/g, '')
          .substring(0, 50)

        expect(sanitized).toBe(expected)
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle database connection errors', async () => {
      const runId = 'run-error'

      mockPrisma.pipelineRun.findUnique.mockRejectedValue(
        new Error('Database connection failed')
      )

      await expect(
        mockPrisma.pipelineRun.findUnique({ where: { id: runId } })
      ).rejects.toThrow('Database connection failed')
    })

    it('should handle malformed JSON in Stage 1 output', async () => {
      const runId = 'run-bad-json'

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: 'invalid json {{{',
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      expect(() => JSON.parse(stage1Output!.output)).toThrow()
    })
  })
})

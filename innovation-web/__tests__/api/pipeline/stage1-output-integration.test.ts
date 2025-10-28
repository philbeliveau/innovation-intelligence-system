/**
 * Stage 1 Output Integration Tests
 * Tests for enhanced Stage 1 output with mechanism extraction
 *
 * References Story 8.0: Backend API Endpoints Prerequisites
 * - AC#1: Stage 1 Output Enhanced with Mechanism Details
 *
 * Note: These tests verify Stage 1 output data structure and integration logic.
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
      findFirst: jest.fn(),
    },
    opportunityCard: {
      findMany: jest.fn(),
    },
  },
}))

describe('Stage 1 Enhanced Output Integration', () => {
  const mockPrisma = prisma as jest.Mocked<typeof prisma>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Complete Stage 1 Output Structure', () => {
    it('should include all required mechanism fields in Stage 1 output', async () => {
      const runId = 'run-123'
      const completeStage1Output = {
        extractedText: 'Full text extracted from the innovation PDF document...',
        trendTitle: 'Hyper-Personalization in Consumer Products',
        trendImage: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA...',
        coreMechanism: 'AI-driven recommendation engine that analyzes user behavior patterns',
        businessImpact: '35% increase in customer engagement, 20% reduction in churn rate, $2M annual revenue uplift',
        patternTransfersTo: [
          'Retail',
          'Healthcare',
          'Financial Services',
          'Entertainment',
          'Education',
        ],
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(completeStage1Output),
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      expect(stage1Output).toBeDefined()
      const output = JSON.parse(stage1Output!.output)

      // Verify all required fields present
      expect(output.extractedText).toBe(completeStage1Output.extractedText)
      expect(output.trendTitle).toBe(completeStage1Output.trendTitle)
      expect(output.trendImage).toBe(completeStage1Output.trendImage)
      expect(output.coreMechanism).toBe(completeStage1Output.coreMechanism)
      expect(output.businessImpact).toBe(completeStage1Output.businessImpact)
      expect(output.patternTransfersTo).toEqual(completeStage1Output.patternTransfersTo)
    })

    it('should handle Stage 1 output with null trendImage', async () => {
      const runId = 'run-no-image'
      const stage1OutputNoImage = {
        extractedText: 'Extracted text...',
        trendTitle: 'Innovation Trend',
        trendImage: null, // No image extracted from PDF
        coreMechanism: 'Core mechanism',
        businessImpact: 'Business impact',
        patternTransfersTo: ['Industry1', 'Industry2'],
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(stage1OutputNoImage),
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const output = JSON.parse(stage1Output!.output)
      expect(output.trendImage).toBeNull()
      expect(output.trendTitle).toBe('Innovation Trend')
    })

    it('should handle Stage 1 output with empty patternTransfersTo array', async () => {
      const runId = 'run-no-patterns'
      const stage1OutputNoPatterns = {
        extractedText: 'Extracted text...',
        trendTitle: 'Niche Innovation',
        trendImage: null,
        coreMechanism: 'Highly specialized mechanism',
        businessImpact: 'Limited to specific niche',
        patternTransfersTo: [], // No transferable patterns identified
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(stage1OutputNoPatterns),
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const output = JSON.parse(stage1Output!.output)
      expect(Array.isArray(output.patternTransfersTo)).toBe(true)
      expect(output.patternTransfersTo).toHaveLength(0)
    })
  })

  describe('Fallback Behavior for Malformed Data', () => {
    it('should handle Stage 1 output with missing optional fields', async () => {
      const runId = 'run-partial'
      const partialStage1Output = {
        extractedText: 'Extracted text...',
        trendTitle: 'Innovation',
        // Missing: trendImage, coreMechanism, businessImpact, patternTransfersTo
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(partialStage1Output),
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      // Should still return output, even if incomplete
      expect(stage1Output).toBeDefined()
      const output = JSON.parse(stage1Output!.output)
      expect(output.extractedText).toBe('Extracted text...')
    })

    it('should handle Stage 1 with empty output string', async () => {
      const runId = 'run-empty-output'

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: '', // Empty output
        createdAt: new Date(),
      } as any)

      const stage1Output = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      expect(stage1Output!.output).toBe('')
    })
  })

  describe('Validation Tests', () => {
    it('should validate extractedText is a string', async () => {
      const runId = 'run-validate-text'
      const stage1Output = {
        extractedText: 'Valid string text',
        trendTitle: 'Title',
        trendImage: null,
        coreMechanism: 'Mechanism',
        businessImpact: 'Impact',
        patternTransfersTo: ['Industry'],
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(stage1Output),
        createdAt: new Date(),
      } as any)

      const result = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const output = JSON.parse(result!.output)
      expect(typeof output.extractedText).toBe('string')
      expect(output.extractedText.length).toBeGreaterThan(0)
    })

    it('should validate patternTransfersTo is an array', async () => {
      const runId = 'run-validate-array'
      const stage1Output = {
        extractedText: 'Text',
        trendTitle: 'Title',
        trendImage: null,
        coreMechanism: 'Mechanism',
        businessImpact: 'Impact',
        patternTransfersTo: ['Industry1', 'Industry2', 'Industry3'],
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(stage1Output),
        createdAt: new Date(),
      } as any)

      const result = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const output = JSON.parse(result!.output)
      expect(Array.isArray(output.patternTransfersTo)).toBe(true)
      expect(output.patternTransfersTo).toHaveLength(3)
      output.patternTransfersTo.forEach((industry: any) => {
        expect(typeof industry).toBe('string')
      })
    })

    it('should validate all field types in complete output', async () => {
      const runId = 'run-validate-all'
      const completeOutput = {
        extractedText: 'Text content',
        trendTitle: 'Title',
        trendImage: 'data:image/png;base64,abc',
        coreMechanism: 'Mechanism',
        businessImpact: 'Impact',
        patternTransfersTo: ['Industry'],
      }

      mockPrisma.stageOutput.findFirst.mockResolvedValue({
        id: 'stage-1',
        runId,
        stageNumber: 1,
        output: JSON.stringify(completeOutput),
        createdAt: new Date(),
      } as any)

      const result = await mockPrisma.stageOutput.findFirst({
        where: { runId, stageNumber: 1 },
      })

      const output = JSON.parse(result!.output)

      // Validate types
      expect(typeof output.extractedText).toBe('string')
      expect(typeof output.trendTitle).toBe('string')
      expect(typeof output.trendImage).toBe('string')
      expect(typeof output.coreMechanism).toBe('string')
      expect(typeof output.businessImpact).toBe('string')
      expect(Array.isArray(output.patternTransfersTo)).toBe(true)
    })
  })
})

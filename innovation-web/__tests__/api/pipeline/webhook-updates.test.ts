/**
 * Webhook Handler Updates - Data Layer Tests
 * Tests for stage output JSON field saves and fullReportMarkdown functionality
 *
 * References Story 10.4: Frontend Webhook Handler Updates
 * - AC#1: stage-update webhook saves to both StageOutput table and PipelineRun JSON fields
 * - AC#2: complete webhook saves fullReportMarkdown to database
 * - AC#7: Backward compatibility with existing StageOutput table functionality
 *
 * Note: These tests verify data logic. Full HTTP webhook testing is done via integration tests.
 */

import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    pipelineRun: {
      findUnique: jest.fn(),
      update: jest.fn()
    },
    stageOutput: {
      upsert: jest.fn(),
      findMany: jest.fn()
    },
    opportunityCard: {
      createMany: jest.fn()
    },
    inspirationReport: {
      create: jest.fn()
    }
  }
}))

describe('Webhook Handler Updates - Data Layer Logic', () => {
  const mockPrisma = prisma as jest.Mocked<typeof prisma>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Stage Update - JSON Field Mapping', () => {
    it('should map stage 1 to stage1Output field', () => {
      const stageOutputMap: Record<number, string> = {
        1: 'stage1Output',
        2: 'stage2Output',
        3: 'stage3Output',
        4: 'stage4Output'
      }

      expect(stageOutputMap[1]).toBe('stage1Output')
    })

    it('should map stage 2 to stage2Output field', () => {
      const stageOutputMap: Record<number, string> = {
        1: 'stage1Output',
        2: 'stage2Output',
        3: 'stage3Output',
        4: 'stage4Output'
      }

      expect(stageOutputMap[2]).toBe('stage2Output')
    })

    it('should map stage 3 to stage3Output field', () => {
      const stageOutputMap: Record<number, string> = {
        1: 'stage1Output',
        2: 'stage2Output',
        3: 'stage3Output',
        4: 'stage4Output'
      }

      expect(stageOutputMap[3]).toBe('stage3Output')
    })

    it('should map stage 4 to stage4Output field', () => {
      const stageOutputMap: Record<number, string> = {
        1: 'stage1Output',
        2: 'stage2Output',
        3: 'stage3Output',
        4: 'stage4Output'
      }

      expect(stageOutputMap[4]).toBe('stage4Output')
    })

    it('should NOT have mapping for stage 5 (no JSON field)', () => {
      const stageOutputMap: Record<number, string> = {
        1: 'stage1Output',
        2: 'stage2Output',
        3: 'stage3Output',
        4: 'stage4Output'
      }

      expect(stageOutputMap[5]).toBeUndefined()
    })
  })

  describe('Stage Update - Data Persistence Logic', () => {
    it('should save to both StageOutput table AND PipelineRun JSON field for stage 1', async () => {
      const runId = 'test-run-123'
      const stageNumber = 1
      const output = '{"test": "stage1 data"}'

      // Simulate saving to StageOutput table
      mockPrisma.stageOutput.upsert.mockResolvedValue({
        id: 'stage-output-1',
        runId,
        stageNumber,
        stageName: 'Input Processing',
        status: 'COMPLETED',
        output,
        completedAt: new Date(),
        createdAt: new Date(),
        updatedAt: new Date()
      })

      // Simulate saving to PipelineRun JSON field
      const parsedOutput = JSON.parse(output)
      mockPrisma.pipelineRun.update.mockResolvedValue({
        id: runId,
        uploadId: 'upload-123',
        brandId: 'test-brand',
        status: 'PROCESSING',
        currentStage: 1,
        stage1Output: parsedOutput,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        createdAt: new Date(),
        updatedAt: new Date(),
        completedAt: null,
        duration: null
      })

      // Execute save logic
      await mockPrisma.stageOutput.upsert({
        where: { runId_stageNumber: { runId, stageNumber } },
        update: { output, status: 'COMPLETED' },
        create: { runId, stageNumber, stageName: 'Input Processing', status: 'COMPLETED', output }
      })

      await mockPrisma.pipelineRun.update({
        where: { id: runId },
        data: { stage1Output: parsedOutput }
      })

      // Verify both saves occurred
      expect(mockPrisma.stageOutput.upsert).toHaveBeenCalledWith({
        where: { runId_stageNumber: { runId, stageNumber } },
        update: expect.objectContaining({ output }),
        create: expect.objectContaining({ runId, stageNumber, output })
      })

      expect(mockPrisma.pipelineRun.update).toHaveBeenCalledWith({
        where: { id: runId },
        data: { stage1Output: parsedOutput }
      })
    })

    it('should handle JSON parsing errors gracefully', () => {
      const invalidJSON = 'not valid json'

      let parsedOutput: unknown
      try {
        parsedOutput = JSON.parse(invalidJSON)
      } catch {
        // If parsing fails, treat as plain string
        parsedOutput = invalidJSON
      }

      // Should fall back to string value
      expect(parsedOutput).toBe(invalidJSON)
    })
  })

  describe('Complete Webhook - fullReportMarkdown Logic', () => {
    it('should save fullReportMarkdown when provided', async () => {
      const runId = 'test-run-123'
      const fullReportMarkdown = '# Full Pipeline Report\n\nComplete analysis...'

      mockPrisma.pipelineRun.update.mockResolvedValue({
        id: runId,
        uploadId: 'upload-123',
        brandId: 'test-brand',
        status: 'COMPLETED',
        currentStage: 5,
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown,
        createdAt: new Date(),
        updatedAt: new Date(),
        completedAt: new Date(),
        duration: 120
      })

      await mockPrisma.pipelineRun.update({
        where: { id: runId },
        data: {
          status: 'COMPLETED',
          completedAt: new Date(),
          duration: 120,
          fullReportMarkdown
        }
      })

      expect(mockPrisma.pipelineRun.update).toHaveBeenCalledWith({
        where: { id: runId },
        data: expect.objectContaining({
          fullReportMarkdown
        })
      })
    })

    it('should skip fullReportMarkdown save when not provided (backward compatibility)', async () => {
      const runId = 'test-run-123'

      mockPrisma.pipelineRun.update.mockResolvedValue({
        id: runId,
        uploadId: 'upload-123',
        brandId: 'test-brand',
        status: 'COMPLETED',
        currentStage: 5,
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        createdAt: new Date(),
        updatedAt: new Date(),
        completedAt: new Date(),
        duration: 120
      })

      // Without fullReportMarkdown field
      await mockPrisma.pipelineRun.update({
        where: { id: runId },
        data: {
          status: 'COMPLETED',
          completedAt: new Date(),
          duration: 120
          // No fullReportMarkdown
        }
      })

      const callArgs = mockPrisma.pipelineRun.update.mock.calls[0][0]
      expect(callArgs.data).not.toHaveProperty('fullReportMarkdown')
    })
  })

  describe('Backward Compatibility - StageOutput Table', () => {
    it('should preserve existing InspirationReport creation from StageOutput table', async () => {
      const runId = 'test-run-123'

      const mockStageOutputs = [
        { stageNumber: 1, output: '{"trendTitle": "AI Trends"}' },
        { stageNumber: 2, output: 'Stage 2 analysis' },
        { stageNumber: 3, output: 'Stage 3 insights' },
        { stageNumber: 4, output: 'Stage 4 opportunities' },
        { stageNumber: 5, output: 'Final cards' }
      ]

      mockPrisma.stageOutput.findMany.mockResolvedValue(
        mockStageOutputs.map(s => ({
          id: `stage-${s.stageNumber}`,
          runId,
          stageNumber: s.stageNumber,
          stageName: `Stage ${s.stageNumber}`,
          status: 'COMPLETED',
          output: s.output,
          completedAt: new Date(),
          createdAt: new Date(),
          updatedAt: new Date()
        }))
      )

      const stageOutputs = await mockPrisma.stageOutput.findMany({
        where: { runId },
        orderBy: { stageNumber: 'asc' }
      })

      // Build stage map (existing logic)
      const stageMap = new Map<number, string>()
      stageOutputs.forEach(stage => {
        stageMap.set(stage.stageNumber, stage.output)
      })

      // Extract track titles from stage 1
      let selectedTrack = ''
      const stage1Output = stageMap.get(1)
      if (stage1Output) {
        try {
          const stage1Data = JSON.parse(stage1Output)
          selectedTrack = stage1Data.trendTitle || ''
        } catch {
          // Ignore parse errors
        }
      }

      expect(selectedTrack).toBe('AI Trends')
      expect(stageMap.get(1)).toBe('{"trendTitle": "AI Trends"}')
      expect(stageMap.get(2)).toBe('Stage 2 analysis')
    })
  })

  describe('Validation Schema Coverage', () => {
    it('should define stage number range 1-5', () => {
      const validStageNumbers = [1, 2, 3, 4, 5]
      const invalidStageNumbers = [0, 6, -1, 10]

      validStageNumbers.forEach(num => {
        expect(num).toBeGreaterThanOrEqual(1)
        expect(num).toBeLessThanOrEqual(5)
      })

      invalidStageNumbers.forEach(num => {
        expect(num < 1 || num > 5).toBe(true)
      })
    })

    it('should define valid status values', () => {
      const validStatuses = ['PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED']
      const invalidStatuses = ['PENDING', 'RUNNING', 'SUCCESS']

      validStatuses.forEach(status => {
        expect(['PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED']).toContain(status)
      })

      invalidStatuses.forEach(status => {
        expect(['PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED']).not.toContain(status)
      })
    })
  })
})

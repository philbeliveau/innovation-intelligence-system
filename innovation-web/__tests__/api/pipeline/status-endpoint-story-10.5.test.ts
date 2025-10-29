/**
 * Story 10.5: Status Endpoint Enhancement Tests
 * Tests for new stage output fields and hasFullReport flag
 */

import { GET } from '@/app/api/pipeline/[runId]/status/route'
import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    pipelineRun: {
      findUnique: jest.fn(),
    },
  },
}))

const mockedPrisma = prisma as jest.Mocked<typeof prisma>

describe('Story 10.5: Status Endpoint Enhancement', () => {
  const mockRunId = 'test-run-123'

  beforeEach(() => {
    jest.clearAllMocks()
  })

  // Helper to create mock request
  const createMockRequest = () => {
    return {} as any // Minimal mock since we don't use request object in the handler
  }

  describe('AC 1-2: Returns stage outputs and hasFullReport', () => {
    it('should return all stage outputs for new runs with JSON data', async () => {
      const mockRun = {
        id: mockRunId,
        status: 'COMPLETED',
        companyName: 'Test Company',
        stage1Output: {
          extractedText: 'Sample text',
          mechanisms: [
            { title: 'Mechanism 1', description: 'Desc 1', categoryTags: ['tag1'] }
          ]
        },
        stage2Output: {
          signals: [
            { title: 'Signal 1', amplifiedInsight: 'Insight 1', strengthFactors: ['factor1'] }
          ]
        },
        stage3Output: {
          insights: [
            { title: 'Insight 1', generalizedInsight: 'General 1', applicationDomains: ['domain1'] }
          ]
        },
        stage4Output: {
          preliminary: [
            { title: 'Prelim 1', contextualizedIdea: 'Idea 1', relevanceToPortfolio: 'High' }
          ]
        },
        fullReportMarkdown: '# Full Report\n\nContent here',
        stageOutputs: [],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      // Verify all stage outputs are present
      expect(data.stage1Output).toEqual(mockRun.stage1Output)
      expect(data.stage2Output).toEqual(mockRun.stage2Output)
      expect(data.stage3Output).toEqual(mockRun.stage3Output)
      expect(data.stage4Output).toEqual(mockRun.stage4Output)

      // Verify hasFullReport flag
      expect(data.hasFullReport).toBe(true)
    })

    it('should return hasFullReport=false when no report exists', async () => {
      const mockRun = {
        id: mockRunId,
        status: 'PROCESSING',
        companyName: 'Test Company',
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        stageOutputs: [],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      expect(data.hasFullReport).toBe(false)
    })
  })

  describe('AC 3: Backward compatibility with old runs', () => {
    it('should return null stage outputs for old runs without JSON data', async () => {
      const mockOldRun = {
        id: mockRunId,
        status: 'COMPLETED',
        companyName: 'Old Company',
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        stageOutputs: [
          {
            stageNumber: 1,
            status: 'COMPLETED',
            output: 'Old stage 1 output',
            completedAt: new Date()
          }
        ],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockOldRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      // All new fields should be null
      expect(data.stage1Output).toBeNull()
      expect(data.stage2Output).toBeNull()
      expect(data.stage3Output).toBeNull()
      expect(data.stage4Output).toBeNull()
      expect(data.hasFullReport).toBe(false)

      // But old stage outputs should still work
      expect(data.stages['1']).toBeDefined()
      expect(data.stages['1'].status).toBe('completed')
    })
  })

  describe('AC 4: Performance - field selection', () => {
    it('should use Prisma select to fetch only needed fields', async () => {
      const mockRun = {
        id: mockRunId,
        status: 'PROCESSING',
        companyName: 'Test Company',
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        stageOutputs: [],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockRun as any)

      await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })

      // Verify Prisma was called with select (not include)
      expect(mockedPrisma.pipelineRun.findUnique).toHaveBeenCalledWith(
        expect.objectContaining({
          select: expect.objectContaining({
            id: true,
            status: true,
            companyName: true,
            stage1Output: true,
            stage2Output: true,
            stage3Output: true,
            stage4Output: true,
            fullReportMarkdown: true,
            stageOutputs: expect.any(Object),
            opportunityCards: expect.any(Object)
          })
        })
      )
    })
  })

  describe('AC 5: TypeScript type safety', () => {
    it('should return response matching PipelineStatusResponse type', async () => {
      const mockRun = {
        id: mockRunId,
        status: 'COMPLETED',
        companyName: 'Test Company',
        stage1Output: {
          extractedText: 'Text',
          mechanisms: []
        },
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: '# Report',
        stageOutputs: [],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      // Verify response structure matches PipelineStatusResponse interface
      expect(data).toHaveProperty('run_id')
      expect(data).toHaveProperty('status')
      expect(data).toHaveProperty('current_stage')
      expect(data).toHaveProperty('stages')
      expect(data).toHaveProperty('stage1Output')
      expect(data).toHaveProperty('stage2Output')
      expect(data).toHaveProperty('stage3Output')
      expect(data).toHaveProperty('stage4Output')
      expect(data).toHaveProperty('hasFullReport')

      expect(typeof data.hasFullReport).toBe('boolean')
    })
  })

  describe('AC 6: Frontend retrospective mode support', () => {
    it('should provide stage outputs for completed runs to enable retrospective display', async () => {
      const mockCompletedRun = {
        id: mockRunId,
        status: 'COMPLETED',
        companyName: 'Test Company',
        stage1Output: {
          extractedText: 'Sample extracted text from PDF',
          mechanisms: [
            {
              title: 'Mechanism Example',
              description: 'Detailed description',
              categoryTags: ['innovation', 'process']
            }
          ]
        },
        stage2Output: {
          signals: [
            {
              title: 'Signal Example',
              amplifiedInsight: 'Amplified insight text',
              strengthFactors: ['factor1', 'factor2']
            }
          ]
        },
        stage3Output: {
          insights: [
            {
              title: 'Insight Example',
              generalizedInsight: 'Generalized insight',
              applicationDomains: ['retail', 'manufacturing']
            }
          ]
        },
        stage4Output: {
          preliminary: [
            {
              title: 'Preliminary Idea',
              contextualizedIdea: 'Contextualized for brand',
              relevanceToPortfolio: 'High relevance'
            }
          ]
        },
        fullReportMarkdown: '# Complete Report\n\nFull markdown content',
        stageOutputs: [],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockCompletedRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      // Verify frontend can use these fields for retrospective display
      expect(data.status).toBe('completed')
      expect(data.stage1Output).toBeDefined()
      expect(data.stage1Output.extractedText).toBe('Sample extracted text from PDF')
      expect(data.stage1Output.mechanisms).toHaveLength(1)

      expect(data.stage2Output).toBeDefined()
      expect(data.stage2Output.signals).toHaveLength(1)

      expect(data.stage3Output).toBeDefined()
      expect(data.stage3Output.insights).toHaveLength(1)

      expect(data.stage4Output).toBeDefined()
      expect(data.stage4Output.preliminary).toHaveLength(1)

      expect(data.hasFullReport).toBe(true)
    })
  })

  describe('Existing functionality preservation', () => {
    it('should maintain existing response fields unchanged', async () => {
      const mockRun = {
        id: mockRunId,
        status: 'PROCESSING',
        companyName: 'Test Company',
        stage1Output: null,
        stage2Output: null,
        stage3Output: null,
        stage4Output: null,
        fullReportMarkdown: null,
        stageOutputs: [
          {
            stageNumber: 2,
            status: 'PROCESSING',
            output: JSON.stringify({ test: 'data' }),
            completedAt: null
          }
        ],
        opportunityCards: []
      }

      mockedPrisma.pipelineRun.findUnique.mockResolvedValue(mockRun as any)

      const response = await GET(createMockRequest(), { params: Promise.resolve({ runId: mockRunId }) })
      const data = await response.json()

      // Verify existing fields are still present and formatted correctly
      expect(data.run_id).toBe(mockRunId)
      expect(data.status).toBe('processing') // Lowercase
      expect(data.current_stage).toBe(2)
      expect(data.brand_name).toBe('Test Company')
      expect(data.stages).toBeDefined()
      expect(data.stages['2']).toBeDefined()
    })
  })
})

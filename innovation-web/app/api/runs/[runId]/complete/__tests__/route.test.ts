/**
 * @jest-environment node
 */
import { NextRequest } from 'next/server'
import { POST } from '../route'
import { prisma } from '@/lib/prisma'

// Mock Prisma
jest.mock('@/lib/prisma', () => ({
  prisma: {
    pipelineRun: {
      findUnique: jest.fn(),
      update: jest.fn(),
    },
    opportunityCard: {
      createMany: jest.fn(),
      create: jest.fn(),
    },
    inspirationReport: {
      create: jest.fn(),
    },
  },
}))

describe('POST /api/runs/[runId]/complete', () => {
  const validSecret = 'test-webhook-secret-12345'
  const mockRunId = 'run-123'
  const mockUserId = 'user-123'

  // Mock environment variable
  beforeAll(() => {
    process.env.WEBHOOK_SECRET = validSecret
  })

  afterAll(() => {
    delete process.env.WEBHOOK_SECRET
  })

  beforeEach(() => {
    jest.clearAllMocks()
  })

  const createMockRequest = (
    secret: string | null,
    body: Record<string, unknown>
  ): NextRequest => {
    const headers = new Headers()
    if (secret !== null) {
      headers.set('X-Webhook-Secret', secret)
    }

    return {
      headers,
      json: async () => body,
    } as unknown as NextRequest
  }

  const mockParams = Promise.resolve({ runId: mockRunId })

  describe('Authentication', () => {
    it('returns 500 when WEBHOOK_SECRET env var is missing', async () => {
      delete process.env.WEBHOOK_SECRET

      const request = createMockRequest(validSecret, {})
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(500)
      expect(data.error).toBe('Server configuration error')

      process.env.WEBHOOK_SECRET = validSecret // Restore
    })

    it('returns 401 when X-Webhook-Secret header is missing', async () => {
      const request = createMockRequest(null, {})
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(401)
      expect(data.error).toBe('Unauthorized')
    })

    it('returns 401 when X-Webhook-Secret is invalid', async () => {
      const request = createMockRequest('wrong-secret', {})
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(401)
      expect(data.error).toBe('Unauthorized')
    })

    it('accepts request when X-Webhook-Secret is valid', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue(null)

      const request = createMockRequest(validSecret, {})
      const response = await POST(request, { params: mockParams })

      expect(response.status).toBe(404) // Run not found, but auth passed
    })
  })

  describe('Run Validation', () => {
    it('returns 404 when runId does not exist', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue(null)

      const request = createMockRequest(validSecret, {})
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(404)
      expect(data.error).toBe('Run not found')
    })

    it('returns 200 when runId exists', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue({
        id: mockRunId,
        userId: mockUserId,
        status: 'PROCESSING',
      })
      ;(prisma.pipelineRun.update as jest.Mock).mockResolvedValue({})
      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 0 })
      ;(prisma.inspirationReport.create as jest.Mock).mockResolvedValue({})

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities: [],
        stageOutputs: {},
      })
      const response = await POST(request, { params: mockParams })

      expect(response.status).toBe(200)
    })
  })

  describe('Idempotency', () => {
    it('returns success when run already COMPLETED', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue({
        id: mockRunId,
        userId: mockUserId,
        status: 'COMPLETED',
      })

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities: [],
      })
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.success).toBe(true)
      expect(data.message).toBe('Run already completed')
      expect(prisma.pipelineRun.update).not.toHaveBeenCalled()
    })

    it('does not create duplicate cards on idempotent call', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue({
        id: mockRunId,
        userId: mockUserId,
        status: 'COMPLETED',
        opportunityCards: [{ id: 'card-1' }],
      })

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities: [{ title: 'Test', markdown: 'Content' }],
      })
      await POST(request, { params: mockParams })

      expect(prisma.opportunityCard.createMany).not.toHaveBeenCalled()
      expect(prisma.opportunityCard.create).not.toHaveBeenCalled()
    })
  })

  describe('Data Processing', () => {
    beforeEach(() => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue({
        id: mockRunId,
        userId: mockUserId,
        status: 'PROCESSING',
      })
      ;(prisma.pipelineRun.update as jest.Mock).mockResolvedValue({})
      ;(prisma.inspirationReport.create as jest.Mock).mockResolvedValue({})
    })

    it('creates opportunity cards with correct data', async () => {
      const opportunities = [
        { number: 1, title: 'Opportunity 1', markdown: 'Content 1' },
        { number: 2, title: 'Opportunity 2', markdown: 'Content 2' },
      ]

      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 2 })

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities,
        stageOutputs: {},
      })
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(prisma.opportunityCard.createMany).toHaveBeenCalledWith({
        data: [
          {
            runId: mockRunId,
            number: 1,
            title: 'Opportunity 1',
            content: 'Content 1',
            isStarred: false,
          },
          {
            runId: mockRunId,
            number: 2,
            title: 'Opportunity 2',
            content: 'Content 2',
            isStarred: false,
          },
        ],
        skipDuplicates: true,
      })
      expect(data.cardsCreated).toBe(2)
    })

    it('skips cards with missing required fields', async () => {
      const opportunities = [
        { number: 1, title: 'Valid', markdown: 'Content' },
        { number: 2, title: '', markdown: 'No title' }, // Missing title
        { number: 3, title: 'No content', markdown: '' }, // Missing markdown
        { number: 4, title: 'Valid 2', markdown: 'Content 2' },
      ]

      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 2 })

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities,
        stageOutputs: {},
      })
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(prisma.opportunityCard.createMany).toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.arrayContaining([
            expect.objectContaining({ title: 'Valid' }),
            expect.objectContaining({ title: 'Valid 2' }),
          ]),
        })
      )
      expect(data.cardsCreated).toBe(2)
      expect(data.totalOpportunities).toBe(4)
    })

    it('creates inspiration report with all stage outputs', async () => {
      const stageOutputs = {
        stage1: { inspirations: [{ title: 'Inspiration 1' }] },
        stage2: { trends: ['Trend 1'] },
        stage3: { lessons: ['Lesson 1'] },
        stage4: { insights: ['Insight 1'] },
        stage5: { opportunities: [] },
      }

      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 0 })

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities: [],
        stageOutputs,
      })
      await POST(request, { params: mockParams })

      expect(prisma.inspirationReport.create).toHaveBeenCalledWith({
        data: {
          runId: mockRunId,
          selectedTrack: 'Inspiration 1',
          nonSelectedTrack: '',
          stage1Output: JSON.stringify(stageOutputs.stage1),
          stage2Output: JSON.stringify(stageOutputs.stage2),
          stage3Output: JSON.stringify(stageOutputs.stage3),
          stage4Output: JSON.stringify(stageOutputs.stage4),
          stage5Output: JSON.stringify(stageOutputs.stage5),
        },
      })
    })

    it('continues processing if card creation fails (fallback)', async () => {
      const opportunities = [
        { number: 1, title: 'Opportunity 1', markdown: 'Content 1' },
        { number: 2, title: 'Opportunity 2', markdown: 'Content 2' },
      ]

      // Simulate bulk insert failure, then individual success
      ;(prisma.opportunityCard.createMany as jest.Mock).mockRejectedValue(
        new Error('Bulk insert failed')
      )
      ;(prisma.opportunityCard.create as jest.Mock).mockResolvedValue({})

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities,
        stageOutputs: {},
      })
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(prisma.opportunityCard.create).toHaveBeenCalledTimes(2)
      expect(data.success).toBe(true)
      expect(data.cardsCreated).toBe(2)
    })

    it('marks run COMPLETED even if report creation fails', async () => {
      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 0 })
      ;(prisma.inspirationReport.create as jest.Mock).mockRejectedValue(
        new Error('Report creation failed')
      )

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration: 120000,
        opportunities: [],
        stageOutputs: {},
      })
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(prisma.pipelineRun.update).toHaveBeenCalledWith({
        where: { id: mockRunId },
        data: expect.objectContaining({
          status: 'COMPLETED',
        }),
      })
      expect(data.success).toBe(true)
    })
  })

  describe('Error Handling', () => {
    it('returns 500 when database error occurs', async () => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockRejectedValue(
        new Error('Database connection failed')
      )

      const request = createMockRequest(validSecret, {})
      const response = await POST(request, { params: mockParams })
      const data = await response.json()

      expect(response.status).toBe(500)
      expect(data.error).toBe('Internal server error')
      expect(data.details).toBe('Database connection failed')
    })

    it('logs detailed error information', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()

      ;(prisma.pipelineRun.findUnique as jest.Mock).mockRejectedValue(
        new Error('Test error')
      )

      const request = createMockRequest(validSecret, {})
      await POST(request, { params: mockParams })

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[Webhook] Error processing completion:',
        expect.any(Error)
      )
      expect(consoleErrorSpy).toHaveBeenCalledWith('[Webhook] Error name:', 'Error')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[Webhook] Error message:',
        'Test error'
      )

      consoleErrorSpy.mockRestore()
    })
  })

  describe('Status Updates', () => {
    beforeEach(() => {
      ;(prisma.pipelineRun.findUnique as jest.Mock).mockResolvedValue({
        id: mockRunId,
        userId: mockUserId,
        status: 'PROCESSING',
      })
      ;(prisma.opportunityCard.createMany as jest.Mock).mockResolvedValue({ count: 0 })
      ;(prisma.inspirationReport.create as jest.Mock).mockResolvedValue({})
    })

    it('updates run with completedAt timestamp', async () => {
      const completedAt = new Date().toISOString()

      const request = createMockRequest(validSecret, {
        completedAt,
        duration: 120000,
        opportunities: [],
        stageOutputs: {},
      })
      await POST(request, { params: mockParams })

      expect(prisma.pipelineRun.update).toHaveBeenCalledWith({
        where: { id: mockRunId },
        data: {
          status: 'COMPLETED',
          completedAt: new Date(completedAt),
          duration: 120000,
        },
      })
    })

    it('updates run with duration in milliseconds', async () => {
      const duration = 180000 // 3 minutes

      const request = createMockRequest(validSecret, {
        completedAt: new Date().toISOString(),
        duration,
        opportunities: [],
        stageOutputs: {},
      })
      await POST(request, { params: mockParams })

      expect(prisma.pipelineRun.update).toHaveBeenCalledWith({
        where: { id: mockRunId },
        data: expect.objectContaining({
          duration: 180000,
        }),
      })
    })
  })
})

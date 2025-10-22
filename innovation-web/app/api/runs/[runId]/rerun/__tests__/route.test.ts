import { POST } from '../route'
import { NextRequest } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { list, put } from '@vercel/blob'
import { runPipeline } from '@/lib/backend-client'
import type { ListBlobResult, PutBlobResult } from '@vercel/blob'

// Mock dependencies
jest.mock('@clerk/nextjs/server')
jest.mock('@vercel/blob')
jest.mock('@/lib/backend-client')

const mockAuth = auth as jest.MockedFunction<typeof auth>
const mockList = list as jest.MockedFunction<typeof list>
const mockPut = put as jest.MockedFunction<typeof put>
const mockRunPipeline = runPipeline as jest.MockedFunction<typeof runPipeline>

describe('POST /api/runs/[runId]/rerun', () => {
  const mockUserId = 'user_123'
  const mockRunId = 'run_456'
  const mockNewRunId = expect.stringMatching(/^run-\d+$/)

  beforeEach(() => {
    jest.clearAllMocks()
    // Mock Date.now() for consistent run IDs
    jest.spyOn(Date, 'now').mockReturnValue(1234567890)
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  const createMockBlobResult = (pathname: string, downloadUrl: string): ListBlobResult => ({
    blobs: [{
      pathname,
      downloadUrl,
      uploadedAt: new Date(),
      url: downloadUrl,
      size: 1024,
    }],
    cursor: undefined,
    hasMore: false,
  })

  const createMockPutResult = (): PutBlobResult => ({
    url: 'https://blob.vercel-storage.com/metadata.json',
    downloadUrl: 'https://blob.vercel-storage.com/metadata.json',
    pathname: 'metadata.json',
    size: 256,
    uploadedAt: new Date(),
  })

  it('should return 401 if user is not authenticated', async () => {
    mockAuth.mockResolvedValue({ userId: null, sessionId: null, orgId: null })

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    const response = await POST(request, { params })
    const data = await response.json()

    expect(response.status).toBe(401)
    expect(data.error).toBe('Unauthorized')
  })

  it('should return 404 if original run not found', async () => {
    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue({ blobs: [], cursor: undefined, hasMore: false })

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    const response = await POST(request, { params })
    const data = await response.json()

    expect(response.status).toBe(404)
    expect(data.error).toContain('Original run not found')
  })

  it('should create new run and trigger pipeline successfully', async () => {
    const blobUrl = 'https://blob.vercel-storage.com/test.pdf'
    const pathname = `${mockUserId}/${mockRunId}_test-document.pdf`

    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue(createMockBlobResult(pathname, blobUrl))
    mockPut.mockResolvedValue(createMockPutResult())
    mockRunPipeline.mockResolvedValue({
      run_id: 'run-1234567890',
      status: 'running',
    })

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    const response = await POST(request, { params })
    const data = await response.json()

    // Verify response
    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(data.newRunId).toMatch(mockNewRunId)
    expect(data.message).toBe('Pipeline rerun initiated')

    // Verify metadata was created
    expect(mockPut).toHaveBeenCalledWith(
      expect.stringMatching(/user_123\/run-\d+_metadata.json/),
      expect.any(String),
      expect.objectContaining({
        access: 'public',
        addRandomSuffix: false,
      })
    )

    // Verify pipeline was triggered
    expect(mockRunPipeline).toHaveBeenCalledWith(
      blobUrl,
      expect.any(String)
    )
  })

  it('should append "(rerun)" to document name', async () => {
    const pathname = `${mockUserId}/${mockRunId}_original-document.pdf`
    const blobUrl = 'https://blob.vercel-storage.com/test.pdf'

    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue(createMockBlobResult(pathname, blobUrl))
    mockPut.mockResolvedValue(createMockPutResult())
    mockRunPipeline.mockResolvedValue({ run_id: 'run-123', status: 'running' })

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    await POST(request, { params })

    // Check that metadata contains rerun suffix
    const putCall = mockPut.mock.calls[0]
    const metadataContent = JSON.parse(putCall[1] as string)
    expect(metadataContent.documentName).toBe('original-document (rerun).pdf')
    expect(metadataContent.isRerun).toBe(true)
    expect(metadataContent.originalRunId).toBe(mockRunId)
  })

  it('should mark run as FAILED if Railway backend trigger fails', async () => {
    const pathname = `${mockUserId}/${mockRunId}_test-document.pdf`
    const blobUrl = 'https://blob.vercel-storage.com/test.pdf'

    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue(createMockBlobResult(pathname, blobUrl))
    mockPut.mockResolvedValue(createMockPutResult())
    mockRunPipeline.mockRejectedValue(new Error('Backend service unavailable'))

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    const response = await POST(request, { params })
    const data = await response.json()

    // Verify error response
    expect(response.status).toBe(500)
    expect(data.error).toContain('Failed to start pipeline rerun')

    // Verify metadata was updated with FAILED status
    expect(mockPut).toHaveBeenCalledTimes(2) // Once for initial, once for failed update
    const failedMetadataCall = mockPut.mock.calls[1]
    const failedMetadata = JSON.parse(failedMetadataCall[1] as string)
    expect(failedMetadata.status).toBe('FAILED')
    expect(failedMetadata.errorMessage).toContain('Backend service unavailable')
  })

  it('should preserve original document URL without re-upload', async () => {
    const originalDocumentUrl = 'https://blob.vercel-storage.com/original-doc.pdf'
    const pathname = `${mockUserId}/${mockRunId}_test.pdf`

    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue(createMockBlobResult(pathname, originalDocumentUrl))
    mockPut.mockResolvedValue(createMockPutResult())
    mockRunPipeline.mockResolvedValue({ run_id: 'run-123', status: 'running' })

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    await POST(request, { params })

    // Verify pipeline was triggered with original URL
    expect(mockRunPipeline).toHaveBeenCalledWith(originalDocumentUrl, expect.any(String))

    // Verify metadata stores original URL
    const putCall = mockPut.mock.calls[0]
    const metadataContent = JSON.parse(putCall[1] as string)
    expect(metadataContent.originalDocumentUrl).toBe(originalDocumentUrl)
  })

  it('should verify user owns original run before allowing rerun', async () => {
    const differentUserId = 'user_999'
    const pathname = `${differentUserId}/${mockRunId}_test.pdf`
    const blobUrl = 'https://blob.vercel-storage.com/test.pdf'

    mockAuth.mockResolvedValue({ userId: mockUserId, sessionId: null, orgId: null })
    mockList.mockResolvedValue(createMockBlobResult(pathname, blobUrl))

    const request = new NextRequest('http://localhost/api/runs/run_456/rerun', {
      method: 'POST',
    })
    const params = Promise.resolve({ runId: mockRunId })

    const response = await POST(request, { params })
    const data = await response.json()

    // User should not find runs from other users
    expect(response.status).toBe(404)
    expect(data.error).toContain('Original run not found')
  })
})

/**
 * @jest-environment node
 */
import { GET } from '../[uploadId]/route'
import { NextRequest } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'

// Mock dependencies
jest.mock('@clerk/nextjs/server')
jest.mock('@/lib/prisma', () => ({
  prisma: {
    user: {
      findUnique: jest.fn()
    },
    document: {
      findFirst: jest.fn()
    }
  }
}))

const mockAuth = auth as jest.MockedFunction<typeof auth>
const mockPrisma = prisma as jest.Mocked<typeof prisma>

describe('GET /api/documents/:uploadId', () => {
  const mockUserId = 'user_123'
  const mockUser = {
    id: 'uuid-user-123',
    clerkId: mockUserId,
    email: 'test@example.com',
    name: 'Test User',
    createdAt: new Date(),
    updatedAt: new Date()
  }

  const mockDocument = {
    id: 'uuid-doc-123',
    userId: 'uuid-user-123',
    fileName: 'test-document.pdf',
    fileSize: 1024000,
    blobUrl: 'https://blob.vercel-storage.com/uploads/1234567890-test.pdf',
    uploadedAt: new Date('2025-01-25T10:00:00Z'),
    createdAt: new Date('2025-01-25T10:00:00Z')
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('should return document metadata for valid uploadId', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)
    mockPrisma.user.findUnique.mockResolvedValue(mockUser)
    mockPrisma.document.findFirst.mockResolvedValue(mockDocument)

    const request = new NextRequest('http://localhost:3000/api/documents/upload-1737799200000')
    const params = Promise.resolve({ uploadId: 'upload-1737799200000' })

    // Act
    const response = await GET(request, { params })
    const data = await response.json()

    // Assert
    expect(response.status).toBe(200)
    expect(data).toEqual({
      blobUrl: mockDocument.blobUrl,
      fileName: mockDocument.fileName,
      fileSize: mockDocument.fileSize,
      uploadedAt: mockDocument.uploadedAt.toISOString()
    })
  })

  it('should return 401 when user is not authenticated', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: null } as any)

    const request = new NextRequest('http://localhost:3000/api/documents/upload-1737799200000')
    const params = Promise.resolve({ uploadId: 'upload-1737799200000' })

    // Act
    const response = await GET(request, { params })
    const data = await response.json()

    // Assert
    expect(response.status).toBe(401)
    expect(data.error).toBe('Unauthorized - Please sign in to continue')
  })

  it('should return 400 for invalid uploadId format', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)

    const request = new NextRequest('http://localhost:3000/api/documents/invalid-id')
    const params = Promise.resolve({ uploadId: 'invalid-id' })

    // Act
    const response = await GET(request, { params })
    const data = await response.json()

    // Assert
    expect(response.status).toBe(400)
    expect(data.error).toBe('Invalid uploadId format')
  })

  it('should return 404 when user not found in database', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)
    mockPrisma.user.findUnique.mockResolvedValue(null)

    const request = new NextRequest('http://localhost:3000/api/documents/upload-1737799200000')
    const params = Promise.resolve({ uploadId: 'upload-1737799200000' })

    // Act
    const response = await GET(request, { params })
    const data = await response.json()

    // Assert
    expect(response.status).toBe(404)
    expect(data.error).toBe('User not found')
  })

  it('should return 404 when document not found', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)
    mockPrisma.user.findUnique.mockResolvedValue(mockUser)
    mockPrisma.document.findFirst.mockResolvedValue(null)

    const request = new NextRequest('http://localhost:3000/api/documents/upload-1737799200000')
    const params = Promise.resolve({ uploadId: 'upload-1737799200000' })

    // Act
    const response = await GET(request, { params })
    const data = await response.json()

    // Assert
    expect(response.status).toBe(404)
    expect(data.error).toBe('Document not found')
  })

  it('should query database with 5-second time window', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)
    mockPrisma.user.findUnique.mockResolvedValue(mockUser)
    mockPrisma.document.findFirst.mockResolvedValue(mockDocument)

    const timestamp = 1737799200000 // 2025-01-25T10:00:00Z
    const request = new NextRequest(`http://localhost:3000/api/documents/upload-${timestamp}`)
    const params = Promise.resolve({ uploadId: `upload-${timestamp}` })

    // Act
    await GET(request, { params })

    // Assert
    expect(mockPrisma.document.findFirst).toHaveBeenCalledWith({
      where: {
        userId: mockUser.id,
        uploadedAt: {
          gte: new Date(timestamp - 5000),
          lte: new Date(timestamp + 5000)
        }
      },
      orderBy: { uploadedAt: 'desc' }
    })
  })

  it('should only return documents belonging to authenticated user', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: mockUserId } as any)
    mockPrisma.user.findUnique.mockResolvedValue(mockUser)
    mockPrisma.document.findFirst.mockResolvedValue(mockDocument)

    const request = new NextRequest('http://localhost:3000/api/documents/upload-1737799200000')
    const params = Promise.resolve({ uploadId: 'upload-1737799200000' })

    // Act
    await GET(request, { params })

    // Assert
    expect(mockPrisma.document.findFirst).toHaveBeenCalledWith(
      expect.objectContaining({
        where: expect.objectContaining({
          userId: mockUser.id
        })
      })
    )
  })
})

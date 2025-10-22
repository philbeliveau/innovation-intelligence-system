/**
 * @jest-environment node
 */

import { POST } from '../route'
import { NextRequest } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'
import { put } from '@vercel/blob'

// Mock dependencies
jest.mock('@clerk/nextjs/server')
jest.mock('@/lib/prisma', () => ({
  prisma: {
    user: {
      upsert: jest.fn(),
    },
    document: {
      create: jest.fn(),
    },
  },
}))
jest.mock('@vercel/blob')

const mockAuth = auth as jest.MockedFunction<typeof auth>
const mockPrisma = prisma as jest.Mocked<typeof prisma>
const mockPut = put as jest.MockedFunction<typeof put>

describe('POST /api/upload - Database Persistence', () => {
  const mockUserId = 'user_123'
  const mockDbUserId = 'db_user_123'
  const mockBlobUrl = 'https://blob.vercel-storage.com/uploads/test.pdf'

  beforeEach(() => {
    jest.clearAllMocks()
    process.env.BLOB_READ_WRITE_TOKEN = 'mock-token'
  })

  const createMockFile = () => {
    const file = new File(['test content'], 'test-document.pdf', {
      type: 'application/pdf',
    })
    Object.defineProperty(file, 'size', { value: 1024 })
    return file
  }

  const createMockRequest = (file: File) => {
    const formData = new FormData()
    formData.append('file', file)

    return {
      formData: jest.fn().mockResolvedValue(formData),
    } as unknown as NextRequest
  }

  it('should save document to database after successful blob upload', async () => {
    // Arrange
    const mockUser = {
      id: mockDbUserId,
      clerkId: mockUserId,
      email: 'test@example.com',
      name: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    const mockDocument = {
      id: 'doc_123',
      userId: mockDbUserId,
      fileName: 'test-document.pdf',
      fileSize: 1024,
      blobUrl: mockBlobUrl,
      uploadedAt: new Date(),
      createdAt: new Date(),
    }

    mockAuth.mockResolvedValue({ userId: mockUserId } as Awaited<ReturnType<typeof auth>>)
    mockPut.mockResolvedValue({ url: mockBlobUrl } as Awaited<ReturnType<typeof put>>)
    mockPrisma.user.upsert.mockResolvedValue(mockUser)
    mockPrisma.document.create.mockResolvedValue(mockDocument)

    const file = createMockFile()
    const request = createMockRequest(file)

    // Act
    const response = await POST(request)
    const data = await response.json()

    // Assert
    expect(response.status).toBe(200)
    expect(data.blob_url).toBe(mockBlobUrl)

    // Verify user upsert was called
    expect(mockPrisma.user.upsert).toHaveBeenCalledWith({
      where: { clerkId: mockUserId },
      update: {},
      create: {
        clerkId: mockUserId,
        email: '',
      },
    })

    // Verify document create was called
    expect(mockPrisma.document.create).toHaveBeenCalledWith({
      data: {
        userId: mockDbUserId,
        fileName: 'test-document.pdf',
        fileSize: 1024,
        blobUrl: mockBlobUrl,
        uploadedAt: expect.any(Date),
      },
    })
  })

  it('should still succeed if database persistence fails', async () => {
    // Arrange
    const mockUser = {
      id: mockDbUserId,
      clerkId: mockUserId,
      email: 'test@example.com',
      name: null,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    mockAuth.mockResolvedValue({ userId: mockUserId } as Awaited<ReturnType<typeof auth>>)
    mockPut.mockResolvedValue({ url: mockBlobUrl } as Awaited<ReturnType<typeof put>>)
    mockPrisma.user.upsert.mockResolvedValue(mockUser)
    mockPrisma.document.create.mockRejectedValue(new Error('Database error'))

    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()

    const file = createMockFile()
    const request = createMockRequest(file)

    // Act
    const response = await POST(request)
    const data = await response.json()

    // Assert
    expect(response.status).toBe(200)
    expect(data.blob_url).toBe(mockBlobUrl)
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Database persistence error:',
      expect.any(Error)
    )

    consoleErrorSpy.mockRestore()
  })

  it('should return 401 if user is not authenticated', async () => {
    // Arrange
    mockAuth.mockResolvedValue({ userId: null } as Awaited<ReturnType<typeof auth>>)

    const file = createMockFile()
    const request = createMockRequest(file)

    // Act
    const response = await POST(request)
    const data = await response.json()

    // Assert
    expect(response.status).toBe(401)
    expect(data.error).toBe('Unauthorized - Please sign in to continue')
    expect(mockPrisma.document.create).not.toHaveBeenCalled()
  })
})

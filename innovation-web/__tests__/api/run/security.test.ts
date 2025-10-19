/**
 * Security Tests for /api/run Route
 * Tests for command injection and path traversal vulnerabilities
 *
 * References QA Gate: docs/qa/gates/3.1-api-routes-pipeline-execution.yml
 * - TEST-001: Zero automated test coverage
 * - SEC-001: Command injection vulnerability (fixed)
 */

import { POST } from '@/app/api/run/route'
import { NextRequest } from 'next/server'
import { cookies } from 'next/headers'

// Mock Next.js modules
jest.mock('next/headers', () => ({
  cookies: jest.fn(),
}))

jest.mock('child_process', () => ({
  execFile: jest.fn((cmd, args, options, callback) => {
    // Simulate successful execution
    callback(null, 'Pipeline started', '')
  }),
}))

jest.mock('fs', () => ({
  writeFileSync: jest.fn(),
}))

describe('POST /api/run - Security Tests', () => {
  const mockCookies = cookies as jest.MockedFunction<typeof cookies>

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('Command Injection Prevention', () => {
    it('should reject company_id with shell metacharacters', async () => {
      const maliciousCompanyIds = [
        'company; rm -rf /',
        'company && cat /etc/passwd',
        'company | echo hacked',
        'company`whoami`',
        'company$(whoami)',
        'company\nmalicious-command',
      ]

      for (const maliciousId of maliciousCompanyIds) {
        mockCookies.mockResolvedValue({
          get: jest.fn(() => ({ value: maliciousId })),
        } as any)

        const request = new NextRequest('http://localhost:3000/api/run', {
          method: 'POST',
          body: JSON.stringify({
            blob_url: 'https://example.com/test.pdf',
            upload_id: 'upload-123',
          }),
        })

        const response = await POST(request)
        const data = await response.json()

        expect(response.status).toBe(400)
        expect(data.error).toBe('Invalid company identifier')
      }
    })

    it('should accept valid alphanumeric company_id with hyphens', async () => {
      const validCompanyIds = [
        'lactalis-canada',
        'columbia-sportswear',
        'company123',
        'test-company-1',
      ]

      for (const validId of validCompanyIds) {
        mockCookies.mockResolvedValue({
          get: jest.fn(() => ({ value: validId })),
        } as any)

        // Mock fetch for blob download
        global.fetch = jest.fn(() =>
          Promise.resolve({
            ok: true,
            arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
          } as Response)
        )

        const request = new NextRequest('http://localhost:3000/api/run', {
          method: 'POST',
          body: JSON.stringify({
            blob_url: 'https://example.com/test.pdf',
            upload_id: 'upload-123',
          }),
        })

        const response = await POST(request)
        const data = await response.json()

        expect(response.status).toBe(200)
        expect(data.run_id).toMatch(/^run-\d+$/)
      }
    })

    it('should use execFile with array args (not shell string)', async () => {
      const { execFile } = require('child_process')

      mockCookies.mockResolvedValue({
        get: jest.fn(() => ({ value: 'test-company' })),
      } as any)

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
        } as Response)
      )

      const request = new NextRequest('http://localhost:3000/api/run', {
        method: 'POST',
        body: JSON.stringify({
          blob_url: 'https://example.com/test.pdf',
          upload_id: 'upload-123',
        }),
      })

      await POST(request)

      // Verify execFile was called (not exec)
      expect(execFile).toHaveBeenCalled()

      // Verify args are passed as array, not string
      const callArgs = execFile.mock.calls[0]
      // Python binary should be from venv
      expect(callArgs[0]).toContain('venv/bin/python3')
      expect(Array.isArray(callArgs[1])).toBe(true)
      expect(callArgs[1]).toContain('--brand')
      expect(callArgs[1]).toContain('test-company')
    })
  })

  describe('Path Traversal Prevention', () => {
    it('should reject blob_url with path traversal attempts', async () => {
      mockCookies.mockResolvedValue({
        get: jest.fn(() => ({ value: 'test-company' })),
      } as any)

      const maliciousUrls = [
        'file:///etc/passwd',
        'file://../../etc/passwd',
        '../../../etc/passwd',
      ]

      for (const maliciousUrl of maliciousUrls) {
        global.fetch = jest.fn(() =>
          Promise.reject(new Error('Invalid URL'))
        )

        const request = new NextRequest('http://localhost:3000/api/run', {
          method: 'POST',
          body: JSON.stringify({
            blob_url: maliciousUrl,
            upload_id: 'upload-123',
          }),
        })

        const response = await POST(request)
        const data = await response.json()

        expect(response.status).toBe(500)
        expect(data.error).toBe('Failed to download uploaded file')
      }
    })
  })

  describe('Input Validation', () => {
    it('should reject requests without blob_url', async () => {
      mockCookies.mockResolvedValue({
        get: jest.fn(() => ({ value: 'test-company' })),
      } as any)

      const request = new NextRequest('http://localhost:3000/api/run', {
        method: 'POST',
        body: JSON.stringify({
          upload_id: 'upload-123',
        }),
      })

      const response = await POST(request)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toContain('Missing required fields')
    })

    it('should reject requests without upload_id', async () => {
      mockCookies.mockResolvedValue({
        get: jest.fn(() => ({ value: 'test-company' })),
      } as any)

      const request = new NextRequest('http://localhost:3000/api/run', {
        method: 'POST',
        body: JSON.stringify({
          blob_url: 'https://example.com/test.pdf',
        }),
      })

      const response = await POST(request)
      const data = await response.json()

      expect(response.status).toBe(400)
      expect(data.error).toContain('Missing required fields')
    })

    it('should reject requests without company cookie', async () => {
      mockCookies.mockResolvedValue({
        get: jest.fn(() => undefined),
      } as any)

      const request = new NextRequest('http://localhost:3000/api/run', {
        method: 'POST',
        body: JSON.stringify({
          blob_url: 'https://example.com/test.pdf',
          upload_id: 'upload-123',
        }),
      })

      const response = await POST(request)
      const data = await response.json()

      expect(response.status).toBe(401)
      expect(data.error).toContain('No company selected')
    })
  })

  describe('Run ID Validation', () => {
    it('should generate valid run_id format', async () => {
      mockCookies.mockResolvedValue({
        get: jest.fn(() => ({ value: 'test-company' })),
      } as any)

      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
        } as Response)
      )

      const request = new NextRequest('http://localhost:3000/api/run', {
        method: 'POST',
        body: JSON.stringify({
          blob_url: 'https://example.com/test.pdf',
          upload_id: 'upload-123',
        }),
      })

      const response = await POST(request)
      const data = await response.json()

      expect(response.status).toBe(200)
      expect(data.run_id).toMatch(/^run-\d+$/)
    })
  })
})

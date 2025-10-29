import '@testing-library/jest-dom'
import { TextEncoder, TextDecoder } from 'util'

// Polyfill for jsPDF (requires TextEncoder/TextDecoder)
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Mock window.matchMedia for components using useReducedMotion
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock Next.js Web APIs for API route testing
if (typeof global.Request === 'undefined') {
  global.Request = class Request {
    constructor(input, init) {
      this.url = input
      this.method = init?.method || 'GET'
      this.headers = new Map(Object.entries(init?.headers || {}))
      this.body = init?.body
    }
  }
}

if (typeof global.Response === 'undefined') {
  global.Response = class Response {
    constructor(body, init) {
      this.body = body
      this.status = init?.status || 200
      this.headers = new Map(Object.entries(init?.headers || {}))
    }

    static json(data, init) {
      return new Response(JSON.stringify(data), {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          ...(init?.headers || {})
        }
      })
    }

    async json() {
      return typeof this.body === 'string' ? JSON.parse(this.body) : this.body
    }
  }
}

if (typeof global.Headers === 'undefined') {
  global.Headers = Map
}

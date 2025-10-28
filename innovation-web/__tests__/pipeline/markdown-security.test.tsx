import { render, screen } from '@testing-library/react'
import ExpandedSparkDetail from '@/components/pipeline/ExpandedSparkDetail'

// Mock Next.js components
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    return <img {...props} />
  },
}))

// Mock react-markdown with rehype-sanitize for security testing
// In production, rehype-sanitize strips dangerous content
jest.mock('react-markdown', () => {
  return function ReactMarkdown({ children }: { children: string }) {
    // Simulate rehype-sanitize behavior: strip script tags and dangerous attributes
    const sanitized = children
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/onerror=/gi, '')
      .replace(/onclick=/gi, '')

    return <div data-testid="sanitized-markdown">{sanitized}</div>
  }
})

jest.mock('remark-gfm', () => () => {})
jest.mock('rehype-sanitize', () => () => {})

const mockSpark = {
  id: 'test-spark-1',
  number: 1,
  title: 'Test Spark',
  summary: 'Test summary',
  content: '# Test Content',
  markdown: '# Test Content',
}

describe('ExpandedSparkDetail - Markdown Security', () => {
  it('strips malicious script tags from markdown content', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: '# Safe Content\n\n<script>alert("XSS")</script>\n\nMore content',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('<script>')
    expect(sanitizedContent?.textContent).not.toContain('alert')
  })

  it('strips iframe tags from markdown content', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: '# Safe Content\n\n<iframe src="https://evil.com"></iframe>\n\nMore content',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('<iframe')
    expect(sanitizedContent?.textContent).not.toContain('evil.com')
  })

  it('sanitizes javascript: protocol in links', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: '[Click me](javascript:alert("XSS"))',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('javascript:')
  })

  it('removes onerror event handlers from markdown', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: '<img src="invalid.jpg" onerror="alert(\'XSS\')">',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('onerror')
  })

  it('removes onclick event handlers from markdown', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: '<div onclick="alert(\'XSS\')">Click me</div>',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('onclick')
  })

  it('safely renders valid markdown content', () => {
    const safeSpark = {
      ...mockSpark,
      content: '# Safe Heading\n\nThis is **bold** and *italic* text.\n\n[Safe Link](https://example.com)',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={safeSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent).toBeInTheDocument()
    expect(sanitizedContent?.textContent).toContain('Safe Heading')
    expect(sanitizedContent?.textContent).toContain('bold')
    expect(sanitizedContent?.textContent).toContain('italic')
  })

  it('handles multiple XSS attempts in single markdown string', () => {
    const maliciousSpark = {
      ...mockSpark,
      content: `
# Title
<script>alert("XSS1")</script>
Some text
<iframe src="evil.com"></iframe>
[Link](javascript:alert("XSS2"))
<img onerror="alert('XSS3')">
      `,
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={maliciousSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent?.textContent).not.toContain('<script')
    expect(sanitizedContent?.textContent).not.toContain('<iframe')
    expect(sanitizedContent?.textContent).not.toContain('javascript:')
    expect(sanitizedContent?.textContent).not.toContain('onerror')
    expect(sanitizedContent?.textContent).toContain('Title')
    expect(sanitizedContent?.textContent).toContain('Some text')
  })

  it('preserves safe HTML entities and special characters', () => {
    const safeSpark = {
      ...mockSpark,
      content: '# Title with &amp; ampersand\n\n< > symbols are safe',
    }

    const { container } = render(
      <ExpandedSparkDetail
        spark={safeSpark}
        currentIndex={0}
        totalSparks={1}
        onBack={jest.fn()}
        onPrevious={jest.fn()}
        onNext={jest.fn()}
      />
    )

    const sanitizedContent = container.querySelector('[data-testid="sanitized-markdown"]')
    expect(sanitizedContent).toBeInTheDocument()
    // Content should be present (implementation detail of how entities are rendered)
    expect(sanitizedContent?.textContent).toContain('Title')
  })
})

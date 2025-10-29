import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'
import { generatePDF } from '@/lib/pdf-generator'
import { pdfDownloadLimiter, getClientIdentifier } from '@/lib/rate-limit'

export async function GET(
  request: NextRequest,
  { params }: { params: { runId: string } }
) {
  try {
    // Check authentication
    const { userId } = await auth()
    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - authentication required' },
        { status: 401 }
      )
    }

    // Check rate limit
    const clientId = getClientIdentifier(request)
    const rateLimit = pdfDownloadLimiter.check(clientId)

    if (!rateLimit.success) {
      const resetDate = new Date(rateLimit.resetAt).toISOString()
      const headers = new Headers()
      headers.set('X-RateLimit-Limit', '10')
      headers.set('X-RateLimit-Remaining', '0')
      headers.set('X-RateLimit-Reset', rateLimit.resetAt.toString())
      headers.set('Retry-After', Math.ceil((rateLimit.resetAt - Date.now()) / 1000).toString())

      return NextResponse.json(
        {
          error: 'Rate limit exceeded',
          message: 'Too many PDF download requests. Please try again later.',
          resetAt: resetDate
        },
        {
          status: 429,
          headers
        }
      )
    }

    const { runId } = params

    // Query pipeline run with required fields
    const run = await prisma.pipelineRun.findUnique({
      where: { id: runId },
      select: {
        fullReportMarkdown: true,
        companyName: true,
        documentName: true,
        completedAt: true
      }
    })

    // Check if run exists
    if (!run) {
      return NextResponse.json(
        { error: 'Pipeline run not found' },
        { status: 404 }
      )
    }

    // Check if report is available
    if (!run.fullReportMarkdown) {
      return NextResponse.json(
        { error: 'Report not available for this pipeline run' },
        { status: 404 }
      )
    }

    // Generate PDF
    const pdfBuffer = await generatePDF({
      markdown: run.fullReportMarkdown,
      companyName: run.companyName || 'Unknown Company',
      documentName: run.documentName || 'Unknown Document',
      generatedAt: run.completedAt || new Date()
    })

    // Sanitize company name for filename (remove special characters, replace spaces with hyphens)
    const sanitizedCompanyName = run.companyName
      ? run.companyName
          .replace(/[^a-zA-Z0-9\s-]/g, '')
          .replace(/\s+/g, '-')
          .replace(/-+/g, '-')
          .toLowerCase()
      : 'unknown-company'

    const filename = `${sanitizedCompanyName}-analysis-report.pdf`

    // Return PDF with appropriate headers including rate limit info
    return new Response(pdfBuffer, {
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': pdfBuffer.byteLength.toString(),
        'Cache-Control': 'public, max-age=31536000, immutable',
        'X-RateLimit-Limit': '10',
        'X-RateLimit-Remaining': rateLimit.remaining.toString(),
        'X-RateLimit-Reset': rateLimit.resetAt.toString()
      }
    })

  } catch (error) {
    console.error('PDF generation failed:', error)

    // Check if it's a timeout error
    if (error instanceof Error && error.message.includes('timeout')) {
      return NextResponse.json(
        { error: 'PDF generation timeout: report too large or server overloaded' },
        { status: 503 }
      )
    }

    return NextResponse.json(
      { error: 'Failed to generate PDF' },
      { status: 500 }
    )
  }
}

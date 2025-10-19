import { NextRequest, NextResponse } from 'next/server'
import pdf from 'pdf-parse-fork'

// Add Node.js runtime configuration for Vercel
export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'
export const maxDuration = 10 // Vercel Hobby plan limit

interface AnalysisResult {
  title: string
  summary: string
  industry: string
  theme: string
  sources: string[]
  tracks: Array<{
    title: string
    summary: string
    icon_url?: string
  }>
}

interface AnalyzeDocumentResponse {
  upload_id: string
  analysis: AnalysisResult
  blob_url: string
  analyzed_at: string
}

export async function POST(request: NextRequest) {
  try {
    // Task 1: Parse and validate request body
    const body = await request.json()
    const { blob_url } = body

    if (!blob_url) {
      return NextResponse.json(
        { error: 'Missing blob_url parameter' },
        { status: 400 }
      )
    }

    // Task 2: Quick PDF validation (download and basic text extraction)
    console.log(`[analyze-document] Validating PDF from: ${blob_url}`)

    let pdfResponse
    try {
      pdfResponse = await fetch(blob_url)

      if (!pdfResponse.ok) {
        console.error(`[analyze-document] Failed to download PDF: ${pdfResponse.status}`)
        return NextResponse.json(
          { error: 'Failed to download document from blob URL' },
          { status: 400 }
        )
      }
    } catch (error) {
      console.error('[analyze-document] Network error downloading PDF:', error)
      return NextResponse.json(
        { error: 'Failed to access blob URL' },
        { status: 400 }
      )
    }

    // Quick text extraction to validate PDF is readable
    let documentText: string
    try {
      const arrayBuffer = await pdfResponse.arrayBuffer()
      const buffer = Buffer.from(arrayBuffer)

      // Parse PDF with pdf-parse-fork (Node.js compatible)
      const data = await pdf(buffer)
      documentText = data.text.slice(0, 500) // Just extract first 500 chars for validation

      if (!documentText || documentText.trim().length === 0) {
        console.error('[analyze-document] PDF contains no extractable text')
        return NextResponse.json(
          { error: 'Document contains no readable text' },
          { status: 400 }
        )
      }

      console.log(`[analyze-document] PDF validated - ${data.text.length} characters total`)
    } catch (error) {
      console.error('[analyze-document] PDF parsing error:', error)
      return NextResponse.json(
        { error: 'Failed to parse PDF document. File may be corrupted or unsupported.' },
        { status: 500 }
      )
    }

    // Task 3: Return immediately with placeholder analysis
    // Real analysis will happen during pipeline execution (Stage 1)
    const upload_id = `upload-${Date.now()}`
    const analyzed_at = new Date().toISOString()

    // Extract first 200 characters as preview
    const preview = documentText.slice(0, 200).trim()

    const analysis: AnalysisResult = {
      title: 'Document Preview',
      summary: `Document uploaded successfully. Preview: ${preview}${documentText.length > 200 ? '...' : ''}`,
      industry: 'pending',
      theme: 'Analysis in progress',
      sources: [],
      tracks: [
        {
          title: 'Track 1 - Analyzing...',
          summary: 'Full analysis will be available after pipeline execution. Click "Launch Innovation Pipeline" to begin.',
          icon_url: ''
        },
        {
          title: 'Track 2 - Analyzing...',
          summary: 'Full analysis will be available after pipeline execution. Click "Launch Innovation Pipeline" to begin.',
          icon_url: ''
        }
      ]
    }

    const response: AnalyzeDocumentResponse = {
      upload_id,
      analysis,
      blob_url,
      analyzed_at
    }

    console.log(`[analyze-document] Returning placeholder analysis with upload_id: ${upload_id}`)

    return NextResponse.json(response)

  } catch (error) {
    // Task 7: Error handling and logging
    console.error('[analyze-document] Unhandled error:', error)

    return NextResponse.json(
      {
        error: 'Failed to analyze document. Please try again.',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

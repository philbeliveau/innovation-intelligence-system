import { NextRequest, NextResponse } from 'next/server'
import { ChatOpenAI } from '@langchain/openai'
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

    // Extract text from PDF for LLM analysis
    let documentText: string
    let fullText: string
    try {
      const arrayBuffer = await pdfResponse.arrayBuffer()
      const buffer = Buffer.from(arrayBuffer)

      // Parse PDF with pdf-parse-fork (Node.js compatible)
      const data = await pdf(buffer)
      fullText = data.text

      // Limit to first 2000 characters for LLM processing (optimized for speed)
      documentText = fullText.slice(0, 2000)

      if (!documentText || documentText.trim().length === 0) {
        console.error('[analyze-document] PDF contains no extractable text')
        return NextResponse.json(
          { error: 'Document contains no readable text' },
          { status: 400 }
        )
      }

      console.log(`[analyze-document] Extracted ${documentText.length} of ${fullText.length} total characters for LLM analysis`)
    } catch (error) {
      console.error('[analyze-document] PDF parsing error:', error)
      return NextResponse.json(
        { error: 'Failed to parse PDF document. File may be corrupted or unsupported.' },
        { status: 500 }
      )
    }

    // Task 3: Configure LangChain with OpenRouter (optimized for speed)
    console.log('[analyze-document] Initializing LLM for document summarization')

    // Validate API key
    if (!process.env.OPENROUTER_API_KEY) {
      console.error('Missing OPENROUTER_API_KEY environment variable')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    const llm = new ChatOpenAI({
      model: process.env.LLM_MODEL || 'deepseek/deepseek-chat',
      apiKey: process.env.OPENROUTER_API_KEY,
      configuration: {
        baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      },
      temperature: 0.7,
      timeout: 30000, // 30 second timeout (optimized)
      maxRetries: 2, // Reduced retries for speed
      maxTokens: 800, // Reduced token limit for faster response
    })

    // Task 4: Create LLM analysis prompt (NO TRACKS - metadata only)
    const analysisPrompt = `You are an innovation intelligence analyst. Analyze the following document excerpt and extract structured metadata.

DOCUMENT EXCERPT (first 2000 characters):
"""
${documentText}
"""

Extract the following information and respond ONLY with valid JSON in this exact format:

{
  "title": "A compelling title capturing the main innovation or trend (10-15 words)",
  "summary": "A concise summary of the document's main points (2-3 sentences, approximately 50 words)",
  "industry": "Primary industry as a single word (e.g., fashion, food, technology, healthcare, sports, retail, finance)",
  "theme": "Main theme or topic in 2-3 words (e.g., 'sustainability innovation', 'customer experience', 'digital transformation')",
  "sources": ["Array of identifiable sources mentioned (website names, publications, companies)"]
}

IMPORTANT REQUIREMENTS:
- Focus on the MAIN innovation or trend in the document
- If no sources are explicitly mentioned, use an empty array: []
- Respond with ONLY valid JSON, no markdown formatting, no code blocks, no additional text`

    // Task 5: Parse and validate LLM response
    console.log('[analyze-document] Sending document to LLM for analysis')

    const upload_id = `upload-${Date.now()}`
    const analyzed_at = new Date().toISOString()

    let analysis: AnalysisResult
    try {
      const result = await llm.invoke(analysisPrompt)

      let content = result.content.toString()

      // Strip markdown code blocks if present
      content = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()

      console.log('[analyze-document] LLM response received, parsing JSON')

      const parsed = JSON.parse(content)

      // Validate required fields
      if (!parsed.title || !parsed.summary || !parsed.industry || !parsed.theme) {
        throw new Error('Missing required fields in LLM response')
      }

      // Ensure sources is an array
      if (!Array.isArray(parsed.sources)) {
        parsed.sources = []
      }

      // Build analysis with LLM-generated metadata and placeholder tracks
      analysis = {
        title: parsed.title,
        summary: parsed.summary,
        industry: parsed.industry,
        theme: parsed.theme,
        sources: parsed.sources,
        tracks: [
          {
            title: 'Track 1',
            summary: 'Full track analysis will be available after pipeline execution.',
            icon_url: ''
          },
          {
            title: 'Track 2',
            summary: 'Full track analysis will be available after pipeline execution.',
            icon_url: ''
          }
        ]
      }

      console.log('[analyze-document] Analysis completed successfully')
      console.log(`[analyze-document] Title: ${analysis.title}`)
      console.log(`[analyze-document] Industry: ${analysis.industry}`)
      console.log(`[analyze-document] Theme: ${analysis.theme}`)

    } catch (error) {
      console.error('[analyze-document] LLM response parsing error:', error)

      // Fallback structure if LLM parsing fails
      const preview = documentText.slice(0, 200).trim()
      const firstSentence = preview.split('.')[0] + '.'

      analysis = {
        title: firstSentence || 'Document Analysis',
        summary: `${preview}${documentText.length > 200 ? '...' : ''}`,
        industry: 'general',
        theme: 'innovation',
        sources: [],
        tracks: [
          {
            title: 'Track 1',
            summary: 'Track analysis will be available after pipeline execution.',
            icon_url: ''
          },
          {
            title: 'Track 2',
            summary: 'Track analysis will be available after pipeline execution.',
            icon_url: ''
          }
        ]
      }
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

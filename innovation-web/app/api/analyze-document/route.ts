import { NextRequest, NextResponse } from 'next/server'
import { ChatOpenAI } from '@langchain/openai'
import * as pdfjs from 'pdfjs-dist/legacy/build/pdf.mjs'

// Configure worker for Node.js environment
if (typeof process !== 'undefined') {
  pdfjs.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/legacy/build/pdf.worker.mjs'
}

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

    // Task 8: Validate environment variables
    if (!process.env.OPENROUTER_API_KEY) {
      console.error('Missing OPENROUTER_API_KEY environment variable')
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      )
    }

    // Task 2: Download PDF from Blob URL
    console.log(`[analyze-document] Downloading PDF from: ${blob_url}`)

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

    // Task 2: Extract text from PDF using pdfjs-dist
    console.log('[analyze-document] Extracting text from PDF')

    let documentText: string
    try {
      const arrayBuffer = await pdfResponse.arrayBuffer()

      // Load PDF document
      const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise

      // Extract text from all pages
      const textParts: string[] = []
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i)
        const textContent = await page.getTextContent()
        const pageText = textContent.items.map((item: any) => item.str).join(' ')
        textParts.push(pageText)
      }

      documentText = textParts.join('\n')

      // Limit to first 4000 characters for LLM processing
      documentText = documentText.slice(0, 4000)

      if (!documentText || documentText.trim().length === 0) {
        console.error('[analyze-document] PDF contains no extractable text')
        return NextResponse.json(
          { error: 'Document contains no readable text' },
          { status: 400 }
        )
      }

      console.log(`[analyze-document] Extracted ${documentText.length} characters from PDF`)
    } catch (error) {
      console.error('[analyze-document] PDF parsing error:', error)
      return NextResponse.json(
        { error: 'Failed to parse PDF document. File may be corrupted or unsupported.' },
        { status: 500 }
      )
    }

    // Task 3: Configure LangChain with OpenRouter
    console.log('[analyze-document] Initializing LLM')

    const llm = new ChatOpenAI({
      model: process.env.LLM_MODEL || 'deepseek/deepseek-chat',
      apiKey: process.env.OPENROUTER_API_KEY,
      configuration: {
        baseURL: process.env.OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1',
      },
      temperature: 0.7,
      timeout: 90000, // 90 second timeout
      maxRetries: 3,
    })

    // Task 4: Create LLM analysis prompt
    const analysisPrompt = `You are an innovation intelligence analyst. Analyze the following document excerpt and extract structured metadata.

DOCUMENT EXCERPT (first 4000 characters):
"""
${documentText}
"""

Extract the following information and respond ONLY with valid JSON in this exact format:

{
  "title": "A compelling title capturing the main innovation or trend (10-15 words)",
  "summary": "A concise summary of the document's main points (2-3 sentences, approximately 50 words)",
  "industry": "Primary industry as a single word (e.g., fashion, food, technology, healthcare, sports, retail, finance)",
  "theme": "Main theme or topic in 2-3 words (e.g., 'sustainability innovation', 'customer experience', 'digital transformation')",
  "sources": ["Array of identifiable sources mentioned (website names, publications, companies)"],
  "tracks": [
    {
      "title": "First ideation track title (concise, 3-6 words)",
      "summary": "Description of this innovation pattern or approach (2-3 sentences)",
      "icon_url": ""
    },
    {
      "title": "Second ideation track title (concise, 3-6 words)",
      "summary": "Description of this distinct innovation pattern or approach (2-3 sentences)",
      "icon_url": ""
    }
  ]
}

IMPORTANT REQUIREMENTS:
- The two tracks must represent DISTINCT innovation patterns, not overlapping concepts
- Each track should offer a different strategic angle or approach
- Tracks should be actionable and specific to the document's content
- If no sources are explicitly mentioned, use an empty array: []
- Leave icon_url as empty string ""
- Respond with ONLY valid JSON, no markdown formatting, no code blocks, no additional text`

    // Task 5: Parse and validate LLM response
    console.log('[analyze-document] Sending document to LLM for analysis')

    let analysis: AnalysisResult
    try {
      const result = await llm.invoke(analysisPrompt)

      let content = result.content.toString()

      // Strip markdown code blocks if present
      content = content.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim()

      console.log('[analyze-document] LLM response received, parsing JSON')

      const parsed = JSON.parse(content)

      // Validate required fields
      if (!parsed.title || !parsed.summary || !parsed.industry || !parsed.theme || !Array.isArray(parsed.tracks)) {
        throw new Error('Missing required fields in LLM response')
      }

      if (parsed.tracks.length !== 2) {
        throw new Error(`Expected 2 tracks, got ${parsed.tracks.length}`)
      }

      for (const track of parsed.tracks) {
        if (!track.title || !track.summary) {
          throw new Error('Track missing required title or summary')
        }
      }

      // Ensure sources is an array
      if (!Array.isArray(parsed.sources)) {
        parsed.sources = []
      }

      analysis = parsed

      console.log('[analyze-document] Analysis completed successfully')
      console.log(`[analyze-document] Title: ${analysis.title}`)
      console.log(`[analyze-document] Industry: ${analysis.industry}`)
      console.log(`[analyze-document] Theme: ${analysis.theme}`)
      console.log(`[analyze-document] Tracks: ${analysis.tracks.map(t => t.title).join(', ')}`)

    } catch (error) {
      console.error('[analyze-document] LLM response parsing error:', error)

      // Fallback structure if parsing fails
      analysis = {
        title: 'Document Analysis (Parsing Error)',
        summary: 'Unable to automatically generate summary. Please review the document manually.',
        industry: 'general',
        theme: 'innovation',
        sources: [],
        tracks: [
          {
            title: 'Track 1',
            summary: 'Automatic track identification failed. Please review document content.',
            icon_url: ''
          },
          {
            title: 'Track 2',
            summary: 'Automatic track identification failed. Please review document content.',
            icon_url: ''
          }
        ]
      }
    }

    // Task 6: Build response object
    const upload_id = `upload-${Date.now()}`
    const analyzed_at = new Date().toISOString()

    const response: AnalyzeDocumentResponse = {
      upload_id,
      analysis,
      blob_url,
      analyzed_at
    }

    console.log(`[analyze-document] Returning analysis with upload_id: ${upload_id}`)

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

'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import DocumentCard from '@/components/DocumentCard'
import { FileViewerPanel } from '@/components/FileViewerPanel'
import PipelineViewer from '@/components/pipeline/PipelineViewer'
import LoadingDocument from '@/components/LoadingDocument'

interface LatentFactor {
  mechanismTitle: string
  mechanismType: string
  constraintEliminated: string
}

interface AnalysisData {
  upload_id: string
  analysis: {
    title: string
    summary: string
    industry: string
    theme: string
    sources: string[]
    latentFactors?: LatentFactor[]
  }
  blob_url: string
  analyzed_at: string
}

export default function AnalyzePage() {
  const params = useParams()
  const router = useRouter()
  const uploadId = params.uploadId as string

  const [blobUrl, setBlobUrl] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string>('')
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [launching, setLaunching] = useState(false)
  const [launchError, setLaunchError] = useState<string>('')
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [isPipelineRunning, setIsPipelineRunning] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)

  useEffect(() => {
    // Try to fetch upload data from sessionStorage first (Story 2.2.1 enhanced format)
    const storedData = sessionStorage.getItem(`upload_${uploadId}`)

    if (storedData) {
      // Found in sessionStorage - use it
      try {
        // Parse new format {blobUrl, fileName, fileSize, uploadedAt}
        const uploadData = JSON.parse(storedData)
        const url = uploadData.blobUrl || storedData // Fallback to old format (plain string)
        setBlobUrl(url)
        setFileName(uploadData.fileName || 'document.pdf')
      } catch {
        // Fallback for old format (plain string blob URL)
        setBlobUrl(storedData)
        setFileName('document.pdf')
      }
    } else {
      // Not in sessionStorage - try to find in upload history from localStorage
      try {
        // Get company_id from cookies to look up history
        const cookies = document.cookie.split(';')
        const companyIdCookie = cookies.find(c => c.trim().startsWith('company_id='))
        const companyId = companyIdCookie?.split('=')[1]

        if (!companyId) {
          setError('Company context not found. Please select a company first.')
          setLoading(false)
          return
        }

        // Import and use upload history functions
        const historyKey = `upload_history_${companyId}`
        const historyData = localStorage.getItem(historyKey)

        if (!historyData) {
          setError('Upload not found. Please upload a file first.')
          setLoading(false)
          return
        }

        const history = JSON.parse(historyData)
        const upload = history.find((u: { upload_id: string }) => u.upload_id === uploadId)

        if (!upload) {
          setError('Upload not found in history.')
          setLoading(false)
          return
        }

        // Found in history - use the stored blob_url and filename
        setBlobUrl(upload.blob_url)
        setFileName(upload.filename || 'document.pdf')
      } catch (err) {
        console.error('Failed to retrieve upload from history:', err)
        setError('Upload not found. Please upload a file first.')
        setLoading(false)
        return
      }
    }

    // Don't proceed if we don't have a blob URL
    if (!blobUrl) {
      return
    }

    // Call analyze-document API
    const analyzeDocument = async () => {
      try {
        const response = await fetch('/api/analyze-document', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ blob_url: blobUrl }),
        })

        if (!response.ok) {
          throw new Error('Failed to analyze document')
        }

        const data = await response.json()
        setAnalysis(data)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to analyze document')
        setLoading(false)
      }
    }

    analyzeDocument()
  }, [uploadId, blobUrl])

  const getErrorMessage = (status: number, defaultMessage: string): string => {
    const errorMap: Record<number, string> = {
      400: 'Invalid request. Please try uploading again.',
      404: 'Brand profile not found. Please select a company.',
      500: 'Pipeline failed to start. Please contact support.',
    }
    return errorMap[status] || defaultMessage
  }

  const handleLaunch = async () => {
    if (!blobUrl || !analysis) return

    setLaunching(true)
    setLaunchError('') // Clear previous errors

    try {
      console.log('[Launch] Starting pipeline with blob:', blobUrl)

      const response = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blob_url: blobUrl,
          upload_id: uploadId,
          selected_tracks: [1],
        }),
      })

      console.log('[Launch] /api/pipeline/run response status:', response.status)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('[Launch] Error response:', errorData)
        const errorMessage = getErrorMessage(
          response.status,
          errorData.error || 'Failed to launch pipeline'
        )
        throw new Error(errorMessage)
      }

      const data = await response.json()
      console.log('[Launch] Pipeline started:', data.run_id)

      // Verify run_id exists before proceeding
      if (!data.run_id) {
        throw new Error('No run ID received from backend')
      }

      // Update state to show pipeline inline (NO NAVIGATION)
      setRunId(data.run_id)
      setIsPipelineRunning(true)
      setLaunching(false)
    } catch (err) {
      console.error('[Launch] Pipeline launch failed:', err)
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to connect. Please check your connection.'
      setLaunchError(errorMessage)
      setLaunching(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    setLoading(true)
    window.location.reload()
  }

  // Loading state
  if (loading) {
    return (
      <main className="min-h-screen bg-[#F5F5F5] flex items-center justify-center">
        <div className="w-full max-w-4xl h-[600px]">
          <LoadingDocument />
        </div>
      </main>
    )
  }

  // Error state
  if (error) {
    return (
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="mb-4 text-2xl font-bold text-gray-900">Analysis Failed</h1>
          <p className="mb-8 text-gray-600">{error}</p>
          <div className="flex justify-center gap-4">
            <Button onClick={handleRetry}>Try Again</Button>
            <Button variant="outline" onClick={() => router.push('/upload')}>
              Back to Upload
            </Button>
          </div>
        </div>
      </main>
    )
  }

  // Success state
  return (
    <main className="min-h-screen bg-gray-50 p-4 sm:p-6">
      <div className="mx-auto max-w-6xl">
        {/* Header: My Board of Ideators - Responsive sizing */}
        <h1 className="mb-6 sm:mb-8 mt-8 sm:mt-12 text-center text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900">
          <span className="italic text-[#4A9B8E]">My</span> Board of Ideators
        </h1>

        {!isPipelineRunning ? (
          /* BEFORE LAUNCH: Document card and launch button */
          <>
            <div className="flex justify-center px-4 sm:px-0">
              {analysis && blobUrl && (
                <DocumentCard
                  title={analysis.analysis.title}
                  summary={analysis.analysis.summary}
                  industry={analysis.analysis.industry}
                  theme={analysis.analysis.theme}
                  sources={analysis.analysis.sources}
                  latentFactors={analysis.analysis.latentFactors}
                  onClick={() => setIsPanelOpen(true)}
                  blobUrl={blobUrl}
                  fileName={fileName}
                />
              )}
            </div>

            {/* Launch Button */}
            <div className="mt-8 flex flex-col items-center gap-4">
              <Button
                size="lg"
                onClick={handleLaunch}
                disabled={launching}
                className="min-w-[200px]"
              >
                {launching && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {launching ? 'Launching Pipeline...' : 'Launch'}
              </Button>

              {/* Error Display */}
              {launchError && (
                <Alert variant="destructive" className="max-w-md">
                  <AlertDescription className="flex items-center justify-between">
                    <span>{launchError}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setLaunchError('')}
                      className="ml-4"
                    >
                      Try Again
                    </Button>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </>
        ) : (
          /* AFTER LAUNCH: Single column mobile, 2-column desktop with document + pipeline */
          <div className="grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-[minmax(320px,480px)_1fr]">
            {/* Left: Document card - Responsive sizing */}
            <div className="flex justify-center lg:justify-start px-4 sm:px-0">
              {analysis && blobUrl && (
                <DocumentCard
                  title={analysis.analysis.title}
                  summary={analysis.analysis.summary}
                  industry={analysis.analysis.industry}
                  theme={analysis.analysis.theme}
                  sources={analysis.analysis.sources}
                  latentFactors={analysis.analysis.latentFactors}
                  onClick={() => setIsPanelOpen(true)}
                  blobUrl={blobUrl}
                  fileName={fileName}
                />
              )}
            </div>

            {/* Right: Pipeline viewer - Responsive spacing */}
            <div className="space-y-4 sm:space-y-6 px-4 sm:px-0">
              {runId && (
                <PipelineViewer
                  runId={runId}
                  inlineMode={true}
                  onComplete={(id) => router.push(`/results/${id}`)}
                  onError={(err) => {
                    setLaunchError(err)
                    setIsPipelineRunning(false)
                  }}
                />
              )}

              {/* Error Recovery UI */}
              {launchError && !launching && (
                <Alert variant="destructive" className="max-w-md">
                  <AlertDescription>
                    <p className="mb-3">{launchError}</p>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={() => {
                          setLaunchError('')
                          setIsPipelineRunning(false)
                          setRunId(null)
                        }}
                      >
                        Retry Pipeline
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push('/upload')}
                      >
                        Return to Upload
                      </Button>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </div>
        )}
      </div>

      {/* File Viewer Panel (Story 2.2.1) */}
      {blobUrl && (
        <FileViewerPanel
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          blobUrl={blobUrl}
          fileName={fileName}
        />
      )}
    </main>
  )
}

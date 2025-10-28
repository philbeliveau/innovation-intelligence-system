'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import { FileViewerPanel } from '@/components/FileViewerPanel'
import PipelineViewer from '@/components/pipeline/PipelineViewer'
import LoadingDocument from '@/components/LoadingDocument'

export default function AnalyzePage() {
  const params = useParams()
  const router = useRouter()
  const uploadId = params.uploadId as string

  const [blobUrl, setBlobUrl] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [launching, setLaunching] = useState(false)
  const [launchError, setLaunchError] = useState<string>('')
  const [isPanelOpen, setIsPanelOpen] = useState(false)
  const [isPipelineRunning, setIsPipelineRunning] = useState(false)
  const [runId, setRunId] = useState<string | null>(null)

  useEffect(() => {
    const loadDocumentData = async () => {
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
          setLoading(false)
          return
        } catch {
          // Fallback for old format (plain string blob URL)
          setBlobUrl(storedData)
          setFileName('document.pdf')
          setLoading(false)
          return
        }
      }

      // Not in sessionStorage - try localStorage
      try {
        // Get company_id from cookies to look up history
        const cookies = document.cookie.split(';')
        const companyIdCookie = cookies.find(c => c.trim().startsWith('company_id='))
        const companyId = companyIdCookie?.split('=')[1]

        if (companyId) {
          const historyKey = `upload_history_${companyId}`
          const historyData = localStorage.getItem(historyKey)

          if (historyData) {
            const history = JSON.parse(historyData)
            const upload = history.find((u: { upload_id: string }) => u.upload_id === uploadId)

            if (upload) {
              // Found in localStorage history
              setBlobUrl(upload.blob_url)
              setFileName(upload.filename || 'document.pdf')
              setLoading(false)
              return
            }
          }
        }
      } catch (err) {
        console.error('Failed to retrieve from localStorage:', err)
      }

      // Final fallback: Query database via API
      try {
        console.log('[Analyze] Querying database for uploadId:', uploadId)
        const response = await fetch(`/api/documents/${uploadId}`)

        if (!response.ok) {
          if (response.status === 404) {
            setError('Document not found. It may have been deleted or you may not have access.')
          } else if (response.status === 401) {
            setError('Please sign in to access this document.')
          } else {
            setError('Failed to load document. Please try again.')
          }
          setLoading(false)
          return
        }

        const documentData = await response.json()
        console.log('[Analyze] Document loaded from database:', documentData.fileName)

        setBlobUrl(documentData.blobUrl)
        setFileName(documentData.fileName)
        setLoading(false)
      } catch (err) {
        console.error('Failed to retrieve document from database:', err)
        setError('Failed to load document. Please upload a file first.')
        setLoading(false)
      }
    }

    loadDocumentData()
  }, [uploadId])

  const getErrorMessage = (status: number, defaultMessage: string): string => {
    const errorMap: Record<number, string> = {
      400: 'Invalid request. Please try uploading again.',
      404: 'Brand profile not found. Please select a company.',
      500: 'Pipeline failed to start. Please contact support.',
    }
    return errorMap[status] || defaultMessage
  }

  const handleLaunch = async () => {
    if (!blobUrl) return

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
      console.log('[Launch] Full API response:', JSON.stringify(data))

      // Verify run_id exists before proceeding
      if (!data.run_id) {
        console.error('[Launch] ERROR: No run_id in response:', data)
        throw new Error('No run ID received from backend')
      }

      // Validate run_id format
      const runIdPattern = /^run-\d+-\d+$/
      if (!runIdPattern.test(data.run_id)) {
        console.error('[Launch] ERROR: Invalid run_id format:', data.run_id)
        throw new Error(`Invalid run ID format: ${data.run_id}`)
      }

      console.log('[Launch] Valid run_id received, setting state to show inline pipeline')
      console.log('[Launch] runId:', data.run_id)
      console.log('[Launch] Setting isPipelineRunning: true')

      // Update state to show pipeline inline (NO NAVIGATION)
      setRunId(data.run_id)
      setIsPipelineRunning(true)
      setLaunching(false)

      console.log('[Launch] State updated. PipelineViewer should render now with runId:', data.run_id)
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
          /* BEFORE LAUNCH: Document info and launch button */
          <>
            <div className="flex justify-center px-4 sm:px-0">
              <div className="max-w-md text-center space-y-4">
                <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">{fileName}</h2>
                  <p className="text-sm text-gray-600 mb-4">
                    Ready to analyze this document with your Board of Ideators
                  </p>
                  {blobUrl && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsPanelOpen(true)}
                      className="w-full"
                    >
                      Preview Document
                    </Button>
                  )}
                </div>
              </div>
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
          /* AFTER LAUNCH: Pipeline viewer */
          <div className="space-y-4 sm:space-y-6 px-4 sm:px-0">
            {runId ? (
              <PipelineViewer
                runId={runId}
                inlineMode={true}
                onComplete={(id) => {
                  console.log('[Analyze] Pipeline completed, redirecting to results:', id)
                  router.push(`/results/${id}`)
                }}
                onError={(err) => {
                  console.error('[Analyze] Pipeline error callback:', err)
                  setLaunchError(err)
                  setIsPipelineRunning(false)
                }}
              />
            ) : null}

            {/* Error Recovery UI */}
            {launchError && !launching && (
              <Alert variant="destructive" className="max-w-md mx-auto">
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

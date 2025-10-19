'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Loader2 } from 'lucide-react'
import DocumentCard from '@/components/DocumentCard'
import TrackCard from '@/components/TrackCard'
import { FileViewerPanel } from '@/components/FileViewerPanel'

interface Track {
  title: string
  summary: string
  icon_url?: string
}

interface AnalysisData {
  upload_id: string
  analysis: {
    title: string
    summary: string
    industry: string
    theme: string
    sources: string[]
    tracks: Track[]
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
  const [selectedTrack, setSelectedTrack] = useState(1)
  const [isPanelOpen, setIsPanelOpen] = useState(false)

  useEffect(() => {
    // Fetch upload data from sessionStorage (Story 2.2.1 enhanced format)
    const storedData = sessionStorage.getItem(`upload_${uploadId}`)

    if (!storedData) {
      setError('Upload not found. Please upload a file first.')
      setLoading(false)
      return
    }

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

    // Call analyze-document API
    const analyzeDocument = async () => {
      try {
        // Use parsed blobUrl from state
        let apiUrl = storedData
        try {
          const uploadData = JSON.parse(storedData)
          apiUrl = uploadData.blobUrl || storedData
        } catch {
          // Use storedData as-is if not JSON
        }

        const response = await fetch('/api/analyze-document', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ blob_url: apiUrl }),
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
    if (!blobUrl || !analysis) return

    setLaunching(true)
    setLaunchError('') // Clear previous errors

    try {
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          blob_url: blobUrl,
          upload_id: uploadId,
          selected_tracks: [selectedTrack],
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = getErrorMessage(
          response.status,
          errorData.error || 'Failed to launch pipeline'
        )
        throw new Error(errorMessage)
      }

      const data = await response.json()
      const runId = data.run_id

      // Store selected track in sessionStorage for pipeline viewer
      sessionStorage.setItem('selected_track', selectedTrack.toString())

      // Store non-selected track data for sidebar display
      const nonSelectedTrack = analysis.analysis.tracks[selectedTrack === 1 ? 1 : 0]
      sessionStorage.setItem('non_selected_track', JSON.stringify(nonSelectedTrack))

      // Brief success state (500ms)
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Navigate to pipeline viewer
      router.push(`/pipeline/${runId}`)
    } catch (err) {
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
      <main className="min-h-screen bg-gray-50 p-8">
        <div className="mx-auto max-w-6xl">
          <div className="mb-8 text-center">
            <Skeleton className="mx-auto mb-4 h-8 w-64" />
            <p className="text-gray-600">Analyzing document...</p>
          </div>
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <div className="space-y-4">
              <Skeleton className="h-48 w-full" />
              <Skeleton className="h-6 w-3/4" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          </div>
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
    <main className="min-h-screen bg-gray-50 p-6">
      <div className="mx-auto max-w-6xl">
        {/* Header: My Board of Ideators */}
        <h1 className="mb-8 text-center text-4xl font-bold text-gray-900">
          <span className="text-teal-600">My</span> Board of Ideators
        </h1>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[280px_1fr]">
          {/* Left: Document Summary Card */}
          <div className="flex justify-center lg:justify-start">
            {analysis && blobUrl && (
              <DocumentCard
                title={analysis.analysis.title}
                summary={analysis.analysis.summary}
                industry={analysis.analysis.industry}
                theme={analysis.analysis.theme}
                sources={analysis.analysis.sources}
                onClick={() => setIsPanelOpen(true)}
                blobUrl={blobUrl}
                fileName={fileName}
              />
            )}
          </div>

          {/* Right: Ideation Tracks */}
          <div>
            <h2 className="mb-4 text-xl font-semibold text-gray-500">
              Ideation Tracks
            </h2>
            <div className="space-y-3">
              {analysis?.analysis.tracks.map((track, index) => (
                <TrackCard
                  key={index}
                  trackNumber={index + 1}
                  title={track.title}
                  summary={track.summary}
                  selected={selectedTrack === index + 1}
                  onSelect={() => setSelectedTrack(index + 1)}
                />
              ))}
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

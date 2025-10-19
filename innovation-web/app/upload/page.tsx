'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'
import { UploadHistorySection } from '@/components/upload/UploadHistorySection'
import { addUploadToHistory } from '@/lib/upload-history'

export default function UploadPage() {
  const router = useRouter()
  const [companyName, setCompanyName] = useState<string>('')
  const [companyId, setCompanyId] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')
  const [fileSize, setFileSize] = useState(0)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [historyKey, setHistoryKey] = useState(0) // Key to force re-render of history section

  // Fetch company context on mount
  useEffect(() => {
    async function checkCompanyContext() {
      try {
        const response = await fetch('/api/onboarding/current-company')
        if (!response.ok) {
          router.push('/')
          return
        }
        const data = await response.json()
        setCompanyName(data.company_name)
        setCompanyId(data.company_id)
      } catch {
        router.push('/')
      }
    }
    checkCompanyContext()
  }, [router])

  // Format file size helper
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  // Handle file upload
  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setFileName(file.name)
    setFileSize(file.size)
    setUploading(true)
    setError('')
    setUploadProgress(0)

    // Simulate progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      clearInterval(progressInterval)

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Upload failed')
      }

      const data = await response.json()
      setUploadProgress(100)

      // Save to sessionStorage with full metadata (Story 2.2.1)
      const uploadData = {
        blobUrl: data.blob_url,
        fileName: file.name,
        fileSize: file.size,
        uploadedAt: new Date().toISOString()
      }
      sessionStorage.setItem(`upload_${data.upload_id}`, JSON.stringify(uploadData))

      // Add to upload history (Story 1.4)
      addUploadToHistory(companyId, {
        upload_id: data.upload_id,
        filename: file.name,
        uploaded_at: Date.now(),
        blob_url: data.blob_url,
        company_id: companyId
      })

      // Show success state
      setUploadSuccess(true)
      setSuccessMessage(`✓ ${file.name} uploaded successfully`)

      // Reset form state after brief success display
      setTimeout(() => {
        setUploading(false)
        setUploadProgress(0)
        setUploadSuccess(false)
        setFileName('')
        setFileSize(0)
        setHistoryKey(prev => prev + 1) // Force history section to reload
      }, 1500)

      // Auto-clear success message
      setTimeout(() => {
        setSuccessMessage('')
      }, 3000)
    } catch (err: unknown) {
      clearInterval(progressInterval)
      setUploading(false)
      setUploadProgress(0)

      // Map errors to user-friendly messages
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      if (errorMessage.includes('Network')) {
        setError('Network error. Please check your connection.')
      } else if (errorMessage.includes('type')) {
        setError('Invalid file type. Please upload PDF, TXT, or MD files.')
      } else if (errorMessage.includes('size')) {
        setError('File too large. Maximum size is 25MB.')
      } else {
        setError('Upload failed. Please try again.')
      }
    }
  }

  // Dropzone configuration
  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 25 * 1024 * 1024, // 25MB
    multiple: false,
    disabled: uploading,
    noClick: true, // Disable default click to handle manually with keyboard
  })

  // Handle keyboard interaction for accessibility (AC 42)
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      if (!uploading) {
        open()
      }
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Company Badge */}
      {companyName && (
        <div className="absolute top-6 right-6">
          <Badge variant="secondary" className="text-sm px-4 py-2">
            {companyName} 🏢
          </Badge>
        </div>
      )}

      {/* Main Content */}
      <div className="flex flex-col items-center px-4 pt-24">
        {/* Title */}
        <h1 className="text-5xl font-bold mb-16 text-center">
          <span className="italic text-[#4A9B8E]">My</span> Board of Ideators
        </h1>

        {/* Upload Zone */}
        <Card className="w-full max-w-2xl p-6 bg-white">
          {!uploading && !uploadSuccess && (
            <>
              <div
                {...getRootProps()}
                onKeyDown={handleKeyDown}
                className={`
                  border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
                  transition-all duration-200
                  ${isDragActive ? 'border-[#4A9B8E] bg-teal-50' : 'border-gray-200 bg-gray-50'}
                  hover:border-gray-300
                `}
                role="button"
                aria-label="Upload file"
                tabIndex={0}
              >
                <input {...getInputProps()} />

                {/* Upload Icon */}
                <div className="flex justify-center mb-2">
                  <div className="w-12 h-12 rounded-full bg-[#4A9B8E]/10 flex items-center justify-center">
                    <svg className="w-6 h-6 text-[#4A9B8E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                </div>

                {/* Upload Heading */}
                <h2 className="text-base font-semibold text-gray-900 mb-1.5">
                  Upload sources
                </h2>

                {/* Drag & drop text with link */}
                <p className="text-sm text-gray-600 mb-1.5">
                  Drag & drop or{' '}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      open()
                    }}
                    className="text-[#4A9B8E] hover:text-[#3A8B7E] underline font-medium"
                  >
                    choose file
                  </button>
                  {' '}to upload
                </p>

                {/* Supported file types */}
                <p className="text-xs text-gray-500 mb-1.5">
                  Supported file types: PDF, txt, Markdown, Audio (e.g. mp3)
                </p>

                {/* Blue link text */}
                <p className="text-sm text-[#4A9B8E] font-medium">
                  Trend Report, Article, etc.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="mt-4">
                <div className="flex gap-2 justify-center flex-wrap">
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Link
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    <span className="text-blue-600">Website</span>
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4 text-red-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                    </svg>
                    <span className="text-red-600">YouTube</span>
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Paste text
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    <span className="text-blue-600">Copied text</span>
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Uploading State */}
          {uploading && !uploadSuccess && (
            <div className="space-y-4 text-center py-8">
              <div className="text-lg font-medium text-gray-700">
                Uploading... {uploadProgress}%
              </div>
              <Progress value={uploadProgress} className="w-full" />
              <div className="text-sm text-gray-600" aria-live="polite">
                {fileName} ({formatFileSize(fileSize)})
              </div>
            </div>
          )}

          {/* Success State */}
          {uploadSuccess && (
            <div className="space-y-4 text-center py-8">
              <div className="text-6xl">✓</div>
              <div className="text-lg font-medium text-green-600">
                Upload complete!
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div
              className="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-lg"
              role="alert"
            >
              <p className="text-red-700 text-sm font-medium">{error}</p>
              <button
                onClick={() => {
                  setError('')
                  setFileName('')
                  setFileSize(0)
                }}
                className="mt-2 text-red-600 text-sm underline hover:text-red-800"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Success Message (Story 1.4) */}
          {successMessage && (
            <div
              className="mt-4 p-4 bg-green-50 border-2 border-green-200 rounded-lg"
              role="alert"
              aria-live="polite"
            >
              <p className="text-green-700 text-sm font-medium">{successMessage}</p>
            </div>
          )}
        </Card>

        {/* Upload History Section (Story 1.4) */}
        {companyId && (
          <div className="w-full max-w-6xl mt-8">
            <UploadHistorySection
              key={historyKey}
              companyId={companyId}
              onHistoryUpdate={() => setHistoryKey(prev => prev + 1)}
            />
          </div>
        )}
      </div>
    </div>
  )
}

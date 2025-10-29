'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'
import { UploadHistorySection } from '@/components/upload/UploadHistorySection'
import { DuplicateUploadDialog } from '@/components/upload/DuplicateUploadDialog'
import { addUploadToHistory, findDuplicateUpload, type UploadMetadata } from '@/lib/upload-history'
import { calculateFileHash } from '@/lib/file-hash'

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

  // Duplicate detection state
  const [checkingDuplicate, setCheckingDuplicate] = useState(false)
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false)
  const [duplicateUpload, setDuplicateUpload] = useState<UploadMetadata | null>(null)
  const [pendingFile, setPendingFile] = useState<File | null>(null)
  const [pendingFileHash, setPendingFileHash] = useState<string>('')

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

  // Handle file upload with duplicate detection
  const onDrop = async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setFileName(file.name)
    setFileSize(file.size)
    setError('')

    // Step 1: Calculate file hash and check for duplicates
    setCheckingDuplicate(true)
    try {
      const contentHash = await calculateFileHash(file)

      // Check localStorage for duplicate
      const duplicate = findDuplicateUpload(companyId, contentHash)

      if (duplicate) {
        // Duplicate found - show dialog
        setCheckingDuplicate(false)
        setDuplicateUpload(duplicate)
        setPendingFile(file)
        setPendingFileHash(contentHash)
        setDuplicateDialogOpen(true)
        return
      }

      // No duplicate - proceed with upload
      setCheckingDuplicate(false)
      await performUpload(file, contentHash)
    } catch (err) {
      setCheckingDuplicate(false)
      console.error('File hashing failed:', err)
      // Proceed without hash if hashing fails
      await performUpload(file, '')
    }
  }

  // Perform the actual upload
  const performUpload = async (file: File, contentHash: string) => {
    setUploading(true)
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
      if (contentHash) {
        formData.append('content_hash', contentHash)
      }

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      clearInterval(progressInterval)

      if (!response.ok) {
        const errorData = await response.json()

        // Handle duplicate error from backend
        if (response.status === 409) {
          setUploading(false)
          setError('This document has already been uploaded.')
          return
        }

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

      // Add to upload history (Story 1.4) with content hash
      addUploadToHistory(companyId, {
        upload_id: data.upload_id,
        filename: file.name,
        uploaded_at: Date.now(),
        blob_url: data.blob_url,
        company_id: companyId,
        content_hash: contentHash || undefined
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

  // Handle "Upload Anyway" from duplicate dialog
  const handleUploadAnyway = async () => {
    if (pendingFile) {
      await performUpload(pendingFile, pendingFileHash)
      setPendingFile(null)
      setPendingFileHash('')
      setDuplicateUpload(null)
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
    disabled: uploading || checkingDuplicate,
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
    <div className="min-h-screen bg-[#F5F5F5] relative overflow-hidden">
      {/* Decorative Teal Circles - Hidden on mobile to prevent overflow */}
      <div className="hidden lg:block absolute inset-0 pointer-events-none" aria-hidden="true">
        {/* Top Left */}
        <div className="absolute top-[10%] left-[15%] w-32 h-32 rounded-full bg-[#5B9A99] opacity-70"></div>
        <div className="absolute top-[25%] left-[8%] w-24 h-24 rounded-full bg-[#6BAAA9] opacity-60"></div>

        {/* Top Right */}
        <div className="absolute top-[12%] right-[18%] w-40 h-40 rounded-full bg-[#5B9A99] opacity-75"></div>
        <div className="absolute top-[8%] right-[35%] w-28 h-28 rounded-full bg-[#6BAAA9] opacity-65"></div>

        {/* Bottom Left */}
        <div className="absolute bottom-[15%] left-[12%] w-36 h-36 rounded-full bg-[#5B9A99] opacity-70"></div>
        <div className="absolute bottom-[8%] left-[25%] w-24 h-24 rounded-full bg-[#6BAAA9] opacity-60"></div>

        {/* Bottom Right */}
        <div className="absolute bottom-[20%] right-[15%] w-32 h-32 rounded-full bg-[#5B9A99] opacity-65"></div>
        <div className="absolute bottom-[10%] right-[8%] w-20 h-20 rounded-full bg-[#6BAAA9] opacity-55"></div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center px-4 pt-12 sm:pt-16 md:pt-24 relative z-10">
        {/* Title - Responsive text sizing */}
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 text-center text-gray-900">
          <span className="italic text-[#5B9A99]">My</span> Board of Ideators
        </h1>

        {/* Subtitle - "Signals to Sparks" in italic teal */}
        <p className="text-base sm:text-lg md:text-xl italic text-[#5B9A99] mb-4">
          Signals to Sparks
        </p>

        {/* Company Name - White rounded rectangle like landing page */}
        {companyName && (
          <div className="mb-8">
            <div className="bg-white px-6 py-2 rounded-lg shadow-sm border border-gray-200">
              <p className="text-base text-gray-800 font-medium">{companyName}</p>
            </div>
          </div>
        )}

        {/* Upload Zone - Responsive sizing */}
        <Card className="w-full max-w-full sm:max-w-xl p-4 sm:p-8 bg-white shadow-lg border-0">
          {!uploading && !uploadSuccess && !checkingDuplicate && (
            <>
              <div
                {...getRootProps()}
                onKeyDown={handleKeyDown}
                className={`
                  border-2 border-dashed rounded-xl p-4 text-center cursor-pointer
                  transition-all duration-300
                  ${isDragActive ? 'border-[#5B9A99] bg-teal-50/50 shadow-lg' : 'border-gray-200 bg-white'}
                  hover:border-[#5B9A99]/50 hover:bg-teal-50/20
                `}
                role="button"
                aria-label="Upload file"
                tabIndex={0}
              >
                <input {...getInputProps()} />

                {/* Upload Heading */}
                <h2 className="text-base font-semibold text-gray-900 mb-2">
                  Upload sources
                </h2>

                {/* Drag & drop text with link */}
                <p className="text-sm text-gray-600 mb-2">
                  Drag & drop or{' '}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      open()
                    }}
                    className="text-[#5B9A99] hover:text-[#4A8887] underline font-medium transition-colors"
                  >
                    choose file
                  </button>
                  {' '}to upload
                </p>

                {/* Supported file types */}
                <p className="text-sm text-gray-500 mb-2">
                  Supported file types: PDF, txt, Markdown, Audio (e.g. mp3)
                </p>

                {/* Blue link text */}
                <p className="text-sm text-[#5B9A99] font-medium">
                  Trend Report, Article, etc.
                </p>
              </div>

              {/* Action Buttons - Grid on mobile for better organization */}
              <div className="mt-6">
                <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2 justify-center">
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    Link
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                    Website
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                    </svg>
                    YouTube
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Paste text
                  </button>
                  <button
                    disabled
                    className="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-200 text-gray-500 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed text-sm"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    Copied text
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Checking Duplicate State */}
          {checkingDuplicate && (
            <div className="space-y-5 text-center py-12">
              <div className="flex justify-center">
                <div className="w-16 h-16 rounded-full bg-[#5B9A99]/10 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-teal-100 border-t-[#5B9A99]"></div>
                </div>
              </div>
              <div className="text-lg font-medium text-gray-800">
                Checking for duplicates...
              </div>
              <div className="text-sm text-gray-600" aria-live="polite">
                {fileName} ({formatFileSize(fileSize)})
              </div>
            </div>
          )}

          {/* Uploading State */}
          {uploading && !uploadSuccess && (
            <div className="space-y-5 text-center py-12">
              <div className="flex justify-center">
                <div className="w-16 h-16 rounded-full bg-[#5B9A99]/10 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-teal-100 border-t-[#5B9A99]"></div>
                </div>
              </div>
              <div className="text-lg font-medium text-gray-800">
                Uploading... {uploadProgress}%
              </div>
              <Progress value={uploadProgress} className="w-full [&>div]:bg-[#5B9A99]" />
              <div className="text-sm text-gray-600" aria-live="polite">
                {fileName} ({formatFileSize(fileSize)})
              </div>
            </div>
          )}

          {/* Success State */}
          {uploadSuccess && (
            <div className="space-y-5 text-center py-12">
              <div className="flex justify-center">
                <div className="w-16 h-16 rounded-full bg-[#5B9A99]/10 flex items-center justify-center">
                  <svg className="w-10 h-10 text-[#5B9A99]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="text-lg font-medium text-[#5B9A99]">
                Upload complete!
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div
              className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl"
              role="alert"
            >
              <p className="text-red-700 text-sm font-medium">{error}</p>
              <button
                onClick={() => {
                  setError('')
                  setFileName('')
                  setFileSize(0)
                }}
                className="mt-2 text-red-600 text-sm underline hover:text-red-800 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Success Message (Story 1.4) */}
          {successMessage && (
            <div
              className="mt-6 p-4 bg-teal-50 border border-[#5B9A99]/30 rounded-xl"
              role="alert"
              aria-live="polite"
            >
              <p className="text-[#5B9A99] text-sm font-medium">{successMessage}</p>
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

      {/* Duplicate Upload Dialog */}
      <DuplicateUploadDialog
        open={duplicateDialogOpen}
        onOpenChange={setDuplicateDialogOpen}
        duplicateUpload={duplicateUpload}
        onUploadAnyway={handleUploadAnyway}
      />
    </div>
  )
}

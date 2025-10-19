'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useDropzone } from 'react-dropzone'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Card } from '@/components/ui/card'

export default function UploadPage() {
  const router = useRouter()
  const [companyName, setCompanyName] = useState<string>('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')
  const [fileSize, setFileSize] = useState(0)
  const [uploadSuccess, setUploadSuccess] = useState(false)

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

      // Save to sessionStorage
      sessionStorage.setItem(`upload_${data.upload_id}`, data.blob_url)

      // Show success state
      setUploadSuccess(true)

      // Redirect after brief delay
      setTimeout(() => {
        router.push(`/analyze/${data.upload_id}`)
      }, 500)
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
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxSize: 25 * 1024 * 1024, // 25MB
    multiple: false,
    disabled: uploading,
  })

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
      <div className="flex flex-col items-center justify-center min-h-screen px-4">
        {/* Title */}
        <h1 className="text-4xl font-bold mb-12 text-center">
          <span className="italic text-teal-600">My</span> Board of Ideators
        </h1>

        {/* Upload Zone */}
        <Card className="w-full max-w-2xl p-8">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
              transition-all duration-200
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'}
              ${uploading ? 'cursor-not-allowed opacity-60' : 'hover:border-gray-400'}
            `}
            role="button"
            aria-label="Upload file"
            tabIndex={0}
          >
            <input {...getInputProps()} />

            {/* Idle State */}
            {!uploading && !uploadSuccess && (
              <div className="space-y-4">
                <div className="text-6xl">📤</div>
                <div className="text-lg text-gray-700">
                  Drag & drop or choose file to upload
                </div>
                <div className="text-sm text-gray-500">
                  Supported types: PDF, txt, Markdown
                </div>
              </div>
            )}

            {/* Uploading State */}
            {uploading && !uploadSuccess && (
              <div className="space-y-4">
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
              <div className="space-y-4">
                <div className="text-6xl">✓</div>
                <div className="text-lg font-medium text-green-600">
                  Upload complete!
                </div>
              </div>
            )}
          </div>

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

          {/* Placeholder Buttons */}
          <div className="flex gap-3 mt-6 justify-center">
            <button
              disabled
              className="px-4 py-2 bg-gray-100 text-gray-400 rounded-md cursor-not-allowed opacity-40"
            >
              Link
            </button>
            <button
              disabled
              className="px-4 py-2 bg-gray-100 text-gray-400 rounded-md cursor-not-allowed opacity-40"
            >
              Website
            </button>
            <button
              disabled
              className="px-4 py-2 bg-gray-100 text-gray-400 rounded-md cursor-not-allowed opacity-40"
            >
              YouTube
            </button>
            <button
              disabled
              className="px-4 py-2 bg-gray-100 text-gray-400 rounded-md cursor-not-allowed opacity-40"
            >
              Paste text
            </button>
          </div>
        </Card>
      </div>
    </div>
  )
}

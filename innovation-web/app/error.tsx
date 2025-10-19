'use client'

import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8 bg-gray-50">
      <Card className="max-w-md w-full p-8 text-center">
        <div className="mb-6">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold mb-4 text-red-600">
            Something went wrong!
          </h2>
          <p className="text-gray-600 mb-2">
            {error.message || 'An unexpected error occurred'}
          </p>
          {error.digest && (
            <p className="text-xs text-gray-400 font-mono mt-2">
              Error ID: {error.digest}
            </p>
          )}
        </div>

        <div className="flex gap-4 justify-center">
          <Button
            onClick={() => reset()}
            variant="default"
            className="px-6"
          >
            Try Again
          </Button>
          <Button
            onClick={() => window.location.href = '/upload'}
            variant="outline"
            className="px-6"
          >
            Return to Upload
          </Button>
        </div>
      </Card>
    </div>
  )
}

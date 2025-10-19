'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'

interface Track {
  trackNumber: number
  title: string
  summary: string
  image?: string
}

export function LeftSidebar() {
  const router = useRouter()
  const [isVisible, setIsVisible] = useState(false)
  const [nonSelectedTrack, setNonSelectedTrack] = useState<Track | null>(null)

  useEffect(() => {
    // Retrieve non-selected track from sessionStorage
    const trackData = sessionStorage.getItem('non_selected_track')
    if (trackData) {
      try {
        setNonSelectedTrack(JSON.parse(trackData))
      } catch (error) {
        console.error('Failed to parse non-selected track data:', error)
      }
    }
  }, [])

  const truncateSummary = (text: string, maxLength: number = 100) => {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  return (
    <>
      {/* Hover detection zone */}
      <div
        className="fixed left-0 top-0 h-full w-5 z-40"
        onMouseEnter={() => setIsVisible(true)}
        aria-hidden="true"
      />

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-full w-60 bg-gray-800 text-white z-50 transition-transform duration-300 ease-in-out overflow-y-auto ${
          isVisible ? 'translate-x-0' : '-translate-x-full'
        }`}
        onMouseLeave={() => setIsVisible(false)}
      >
        <div className="p-4 space-y-4">
          {/* Home Button */}
          <Button
            variant="ghost"
            className="w-full justify-start text-white hover:bg-gray-700"
            onClick={() => router.push('/upload')}
          >
            🏠 Home
          </Button>

          {/* Ideation Tracks Section */}
          {nonSelectedTrack && (
            <div className="mt-6">
              <h3 className="text-sm font-semibold mb-2 text-gray-300">
                Ideation Tracks
              </h3>
              <Card className="bg-gray-100 p-3 opacity-80">
                <div className="flex items-start gap-2">
                  <span className="text-2xl font-bold text-gray-400">
                    {nonSelectedTrack.trackNumber}
                  </span>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-800">
                      {nonSelectedTrack.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {truncateSummary(nonSelectedTrack.summary)}
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

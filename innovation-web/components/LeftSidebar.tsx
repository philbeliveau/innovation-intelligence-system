'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { useRuns } from '@/lib/use-runs'
import { formatRelativeTime } from '@/lib/format-relative-time'
import type { RunStatus } from '@/app/api/runs/route'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'

interface Track {
  trackNumber: number
  title: string
  summary: string
  image?: string
}

export function LeftSidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const [isVisible, setIsVisible] = useState(true) // Start visible for debugging
  const [nonSelectedTrack, setNonSelectedTrack] = useState<Track | null>(null)
  const [isMobile, setIsMobile] = useState(false)

  // Enable polling on all pages to show runs in sidebar
  const { runs, loading, error } = useRuns({
    pageSize: 5,
    pollingInterval: 10000,
    enabled: true, // Always fetch runs
  })

  // Detect mobile on mount
  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  useEffect(() => {
    // Clear track data when on home/upload page
    if (pathname === '/' || pathname === '/upload') {
      sessionStorage.removeItem('non_selected_track')
      setNonSelectedTrack(null)
      return
    }

    // Retrieve non-selected track from sessionStorage on other pages
    const trackData = sessionStorage.getItem('non_selected_track')
    if (trackData) {
      try {
        setNonSelectedTrack(JSON.parse(trackData))
      } catch (error) {
        console.error('Failed to parse non-selected track data:', error)
      }
    }
  }, [pathname])

  const handleHomeClick = () => {
    // Clear track data when navigating home
    sessionStorage.removeItem('non_selected_track')
    setNonSelectedTrack(null)
    router.push('/upload')
  }

  const truncateDocumentName = (text: string, maxLength: number = 20) => {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
  }

  const getStatusBadge = (status: RunStatus) => {
    switch (status) {
      case 'PROCESSING':
        return (
          <span className="flex items-center gap-1 text-blue-600">
            <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </span>
        )
      case 'COMPLETED':
        return <span className="text-green-600">✅</span>
      case 'FAILED':
        return <span className="text-red-600">❌</span>
      case 'CANCELLED':
        return <span className="text-gray-400">⭕</span>
      default:
        return null
    }
  }

  const handleRunClick = (runId: string) => {
    router.push(`/runs/${runId}`)
    if (isMobile) setIsVisible(false)
  }

  const handleViewAllRuns = () => {
    router.push('/runs')
    if (isMobile) setIsVisible(false)
  }

  return (
    <>
      {/* Mobile: Floating toggle button */}
      {isMobile && !isVisible && (
        <button
          onClick={() => setIsVisible(true)}
          className="fixed left-4 top-4 z-50 bg-white p-2 rounded-full shadow-lg border border-gray-200 hover:bg-gray-50"
          aria-label="Open menu"
        >
          <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}

      {/* Desktop: Hover detection zone */}
      {!isMobile && (
        <div
          className="fixed left-0 top-0 h-full w-5 z-40"
          onMouseEnter={() => setIsVisible(true)}
          aria-hidden="true"
        />
      )}

      {/* Mobile overlay backdrop */}
      {isMobile && isVisible && (
        <div
          className="fixed inset-0 bg-black/20 z-40"
          onClick={() => setIsVisible(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar - Mobile: slide from left, Desktop: hover reveal */}
      <div
        className={`fixed ${isMobile ? 'left-0 top-0 bottom-0' : 'left-4 top-1/2 -translate-y-1/2'} z-50 transition-transform duration-300 ease-in-out ${
          isVisible ? 'translate-x-0' : '-translate-x-full'
        }`}
        onMouseLeave={() => !isMobile && setIsVisible(false)}
        style={{ minWidth: isMobile ? 'auto' : '240px' }}
      >
        <div className={`flex bg-white ${isMobile ? 'h-full flex-col p-4' : 'w-full'} px-1.5 py-1.5 shadow-lg ${isMobile ? 'rounded-r-2xl' : 'rounded-2xl'}`}>
          {/* Mobile: Close button */}
          {isMobile && (
            <button
              onClick={() => setIsVisible(false)}
              className="self-end mb-4 p-2 hover:bg-gray-100 rounded-full"
              aria-label="Close menu"
            >
              <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}

          <div className={`rounded-2xl w-full px-1.5 py-1.5 md:px-3 md:py-3 flex flex-col gap-4`}>
            {/* Home Button */}
            <button
              title="Go to the home page"
              onClick={handleHomeClick}
              className="text-gray-600 hover:text-black border-2 flex items-center justify-center p-2.5 border-transparent bg-gray-50 shadow-sm hover:shadow-md focus:opacity-100 focus:outline-none active:shadow-inner font-medium rounded-full text-sm"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-5 h-5"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"
                ></path>
              </svg>
            </button>

            {/* Ideation Track Button (if track exists) */}
            {nonSelectedTrack && (
              <button
                title={`Track ${nonSelectedTrack.trackNumber}: ${nonSelectedTrack.title}`}
                className="text-gray-600 hover:text-black border-2 flex items-center justify-center p-2.5 border-transparent bg-gray-50 shadow-sm hover:shadow-md focus:opacity-100 focus:outline-none active:shadow-inner font-medium rounded-full text-sm"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-5 h-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"
                  ></path>
                  <path
                    fillRule="evenodd"
                    d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                    clipRule="evenodd"
                  ></path>
                </svg>
              </button>
            )}

            {/* Authentication UI - Moved to top for visibility */}
            <SignedOut>
              <SignInButton mode="modal">
                <button
                  title="Sign In"
                  className="text-gray-600 hover:text-black border-2 flex items-center justify-center p-2.5 border-transparent bg-gray-50 shadow-sm hover:shadow-md focus:opacity-100 focus:outline-none active:shadow-inner font-medium rounded-full text-sm"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-5 h-5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center justify-center p-2.5 bg-gray-50 rounded-full shadow-sm">
                <UserButton
                  appearance={{
                    elements: {
                      avatarBox: "w-5 h-5"
                    }
                  }}
                />
              </div>
            </SignedIn>

            {/* My Runs Section */}
            <SignedIn>
              <div className="w-full border-t border-gray-200 my-2" />
              <div className="w-full">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <h3 className="text-xs font-semibold text-gray-500 px-2 mb-2 cursor-help inline-flex items-center gap-1">
                        My Runs
                        <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </h3>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-xs">
                      <p className="text-xs">Full status tracking coming soon. Currently showing upload history.</p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>

                {/* Loading State */}
                {loading && (
                  <div className="space-y-2">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse bg-gray-100 rounded-lg p-2 h-16" />
                    ))}
                  </div>
                )}

                {/* Error State */}
                {error && !loading && (
                  <div className="text-xs text-red-600 px-2 py-1 bg-red-50 rounded-lg">
                    {error}
                  </div>
                )}

                {/* Runs List */}
                {!loading && !error && runs.length === 0 && (
                  <div className="text-xs text-gray-400 px-2 py-1">
                    No runs yet
                  </div>
                )}

                {!loading && !error && runs.length > 0 && (
                  <div className="space-y-1">
                    {runs.map((run) => (
                      <button
                        key={run.id}
                        onClick={() => handleRunClick(run.id)}
                        className="w-full text-left p-2 rounded-lg hover:bg-gray-50 transition-colors border border-transparent hover:border-gray-200"
                        title={`${run.documentName} - ${run.companyName}`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium text-gray-900 truncate">
                              {truncateDocumentName(run.documentName)}
                            </div>
                            <div className="text-xs text-gray-500 truncate">
                              {run.companyName}
                            </div>
                            <div className="text-xs text-gray-400 mt-1">
                              {formatRelativeTime(run.createdAt)}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            {getStatusBadge(run.status)}
                            {run.cardCount > 0 && (
                              <span className="text-xs text-gray-500">
                                {run.cardCount} cards
                              </span>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* View All Runs Link */}
                {runs.length > 0 && (
                  <button
                    onClick={handleViewAllRuns}
                    className="w-full mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium py-1 px-2 rounded hover:bg-blue-50 transition-colors"
                  >
                    View All Runs →
                  </button>
                )}
              </div>
            </SignedIn>
          </div>
        </div>
      </div>
    </>
  )
}

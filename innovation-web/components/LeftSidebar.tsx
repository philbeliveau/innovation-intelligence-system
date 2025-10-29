'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'
import { useRuns } from '@/lib/use-runs'
import { formatRelativeTime } from '@/lib/format-relative-time'
import type { RunStatus } from '@/app/api/pipeline/route'
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip'
import { useSidebarContext } from './LayoutWithSidebar'

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
  const { isSidebarSticky: isSticky, setIsSidebarSticky: setIsSticky } = useSidebarContext()

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
        return <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-[#5B9A99]" /></span>
      case 'FAILED':
        return <span className="flex items-center"><div className="w-2 h-2 rounded-full bg-red-600" /></span>
      case 'CANCELLED':
        return <span className="flex items-center"><div className="w-2 h-2 rounded-full border-2 border-gray-400" /></span>
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

      {/* Sidebar - Mobile: slide from left, Desktop: hover reveal or sticky */}
      <div
        className={`fixed ${isMobile ? 'left-0 top-0 bottom-0' : isSticky ? 'left-0 top-0 bottom-0' : 'left-4 top-1/2 -translate-y-1/2'} z-50 transition-all duration-300 ease-in-out ${
          isVisible ? 'translate-x-0' : '-translate-x-full'
        }`}
        onMouseLeave={() => !isMobile && !isSticky && setIsVisible(false)}
        style={{ minWidth: isMobile ? 'auto' : '220px' }}
      >
        <div className={`flex bg-white ${isMobile ? 'h-full flex-col p-4' : isSticky ? 'h-full flex-col py-4 pr-4 pl-2' : 'w-56 p-4'} shadow-md shadow-teal-200/50 ${isMobile ? 'rounded-r-md' : isSticky ? 'rounded-r-md' : 'rounded-md'}`}>
          {/* Header: Close button (mobile) + Sticky toggle (desktop) */}
          <div className="flex items-center justify-between mb-4">
            {isMobile && (
              <button
                onClick={() => setIsVisible(false)}
                className="p-2 hover:bg-teal-50 rounded-full transition-all"
                aria-label="Close menu"
              >
                <svg className="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
            {!isMobile && (
              <button
                onClick={() => setIsSticky(!isSticky)}
                className="ml-auto p-1.5 hover:bg-teal-50 rounded-full transition-all"
                title={isSticky ? 'Unstick sidebar' : 'Stick sidebar'}
                aria-label={isSticky ? 'Unstick sidebar' : 'Stick sidebar'}
              >
                {isSticky ? (
                  // Locked icon
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <rect x="5" y="11" width="14" height="10" rx="2" stroke="#5B9A99" strokeWidth="2"/>
                    <path d="M8 11V7a4 4 0 0 1 8 0v4" stroke="#5B9A99" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="12" cy="16" r="1.5" fill="#5B9A99"/>
                  </svg>
                ) : (
                  // Unlocked icon
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <rect x="5" y="11" width="14" height="10" rx="2" stroke="#9CA3AF" strokeWidth="2"/>
                    <path d="M8 11V7a4 4 0 0 1 8 0v3" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round"/>
                    <circle cx="12" cy="16" r="1.5" fill="#9CA3AF"/>
                  </svg>
                )}
              </button>
            )}
          </div>

          <ul className="w-full flex flex-col gap-1.5">
            {/* Home Button */}
            <li className="flex-center cursor-pointer w-full whitespace-nowrap">
              <button
                title="Go to the home page"
                onClick={handleHomeClick}
                className="flex size-full gap-2 p-2.5 group text-sm font-semibold rounded-full bg-cover hover:bg-teal-50 hover:shadow-inner focus:bg-[#5B9A99] focus:text-white text-gray-700 transition-all ease-linear"
              >
                <svg
                  stroke="#000000"
                  className="size-5 group-focus:fill-white group-focus:stroke-white"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="#000000"
                >
                  <g strokeWidth="0"></g>
                  <g strokeLinejoin="round" strokeLinecap="round"></g>
                  <g>
                    <path d="M14,10V22H4a2,2,0,0,1-2-2V10Z"></path>
                    <path d="M22,10V20a2,2,0,0,1-2,2H16V10Z"></path>
                    <path d="M22,4V8H2V4A2,2,0,0,1,4,2H20A2,2,0,0,1,22,4Z"></path>
                  </g>
                </svg>
                Dashboard
              </button>
            </li>

            {/* Ideation Track Button (if track exists) */}
            {nonSelectedTrack && (
              <li className="flex-center cursor-pointer w-full whitespace-nowrap">
                <button
                  title={`Track ${nonSelectedTrack.trackNumber}: ${nonSelectedTrack.title}`}
                  className="flex size-full gap-2 p-2.5 group text-sm font-semibold rounded-full bg-cover hover:bg-teal-50 hover:shadow-inner focus:bg-[#5B9A99] focus:text-white text-gray-700 transition-all ease-linear"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="size-5 group-focus:fill-white"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"></path>
                    <path
                      fillRule="evenodd"
                      d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                  Track {nonSelectedTrack.trackNumber}
                </button>
              </li>
            )}

            {/* Authentication UI */}
            <SignedOut>
              <li className="flex-center cursor-pointer w-full whitespace-nowrap">
                <SignInButton mode="modal">
                  <button
                    title="Sign In"
                    className="flex size-full gap-2 p-2.5 group text-sm font-semibold rounded-full bg-cover hover:bg-teal-50 hover:shadow-inner focus:bg-[#5B9A99] focus:text-white text-gray-700 transition-all ease-linear"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      className="size-5"
                    >
                      <path
                        className="group-focus:fill-white"
                        fill="#000"
                        d="M5 2C3.34315 2 2 3.34315 2 5V19C2 20.6569 3.34315 22 5 22H14.5C15.8807 22 17 20.8807 17 19.5V16.7326C16.8519 16.647 16.7125 16.5409 16.5858 16.4142C15.9314 15.7598 15.8253 14.7649 16.2674 14H13C11.8954 14 11 13.1046 11 12C11 10.8954 11.8954 10 13 10H16.2674C15.8253 9.23514 15.9314 8.24015 16.5858 7.58579C16.7125 7.4591 16.8519 7.35296 17 7.26738V4.5C17 3.11929 15.8807 2 14.5 2H5Z"
                      />
                      <path
                        className="group-focus:fill-white"
                        fill="#000000"
                        d="M17.2929 14.2929C16.9024 14.6834 16.9024 15.3166 17.2929 15.7071C17.6834 16.0976 18.3166 16.0976 18.7071 15.7071L21.6201 12.7941C21.6351 12.7791 21.6497 12.7637 21.6637 12.748C21.87 12.5648 22 12.2976 22 12C22 11.7024 21.87 11.4352 21.6637 11.252C21.6497 11.2363 21.6351 11.2209 21.6201 11.2059L18.7071 8.29289C18.3166 7.90237 17.6834 7.90237 17.2929 8.29289C16.9024 8.68342 16.9024 9.31658 17.2929 9.70711L18.5858 11H13C12.4477 11 12 11.4477 12 12C12 12.5523 12.4477 13 13 13H18.5858L17.2929 14.2929Z"
                      />
                    </svg>
                    Login
                  </button>
                </SignInButton>
              </li>
            </SignedOut>
            <SignedIn>
              <li className="flex-center cursor-pointer w-full whitespace-nowrap">
                <button className="flex size-full gap-2 p-2.5 group text-sm font-semibold rounded-full bg-cover hover:bg-teal-50 hover:shadow-inner focus:bg-[#5B9A99] focus:text-white text-gray-700 transition-all ease-linear items-center">
                  <UserButton
                    appearance={{
                      elements: {
                        avatarBox: "w-5 h-5"
                      }
                    }}
                  />
                  <span>Settings</span>
                </button>
              </li>
            </SignedIn>

            {/* My Runs Section */}
            <SignedIn>
              <li className="w-full border-t border-gray-200 my-2" />
              <li className="w-full px-1">
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <h3 className="text-[10px] font-semibold text-gray-500 mb-1.5 cursor-help inline-flex items-center gap-1">
                        My Runs
                        <svg className="w-2.5 h-2.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                  <div className="text-[10px] text-gray-400 px-1 py-1">
                    No runs yet
                  </div>
                )}

                {!loading && !error && runs.length > 0 && (
                  <div className="space-y-1">
                    {runs.map((run) => (
                      <button
                        key={run.id}
                        onClick={() => handleRunClick(run.id)}
                        className="w-full text-left p-1.5 rounded-md hover:bg-teal-50 transition-colors border border-transparent hover:border-teal-200"
                        title={`${run.documentName} - ${run.companyName}`}
                      >
                        <div className="flex items-start justify-between gap-1">
                          <div className="flex-1 min-w-0">
                            <div className="text-[10px] font-medium text-gray-900 truncate leading-tight">
                              {truncateDocumentName(run.documentName)}
                            </div>
                            <div className="text-[9px] text-gray-500 truncate leading-tight">
                              {run.companyName}
                            </div>
                            <div className="text-[9px] text-gray-400 mt-0.5 leading-tight">
                              {formatRelativeTime(run.createdAt)}
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-0.5">
                            {getStatusBadge(run.status)}
                            {run.cardCount > 0 && (
                              <span className="text-[9px] text-gray-500">
                                {run.cardCount}
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
                    className="w-full mt-1.5 text-[10px] text-[#5B9A99] hover:text-[#4A8887] font-medium py-1 px-1 rounded hover:bg-teal-50 transition-colors"
                  >
                    View All →
                  </button>
                )}
              </li>
            </SignedIn>
          </ul>
        </div>
      </div>
    </>
  )
}

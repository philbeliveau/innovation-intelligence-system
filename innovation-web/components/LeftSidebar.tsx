'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs'

interface Track {
  trackNumber: number
  title: string
  summary: string
  image?: string
}

export function LeftSidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const [isVisible, setIsVisible] = useState(false)
  const [nonSelectedTrack, setNonSelectedTrack] = useState<Track | null>(null)
  const [isMobile, setIsMobile] = useState(false)

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

  const truncateSummary = (text: string, maxLength: number = 100) => {
    if (!text) return ''
    if (text.length <= maxLength) return text
    return text.slice(0, maxLength) + '...'
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
      >
        <div className={`flex bg-white ${isMobile ? 'h-full flex-col p-4' : 'w-fit'} px-1.5 py-1.5 shadow-lg ${isMobile ? 'rounded-r-2xl' : 'rounded-2xl'}`}>
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

            {/* Authentication UI */}
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
          </div>
        </div>
      </div>
    </>
  )
}

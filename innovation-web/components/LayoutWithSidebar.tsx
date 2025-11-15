'use client'

import { createContext, useContext, useState, ReactNode, useEffect } from 'react'

interface SidebarContextType {
  isSidebarSticky: boolean
  setIsSidebarSticky: (sticky: boolean) => void
  isMobile: boolean
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined)

export function useSidebarContext() {
  const context = useContext(SidebarContext)
  if (!context) {
    throw new Error('useSidebarContext must be used within SidebarProvider')
  }
  return context
}

export function LayoutWithSidebar({ children }: { children: ReactNode }) {
  const [isSidebarSticky, setIsSidebarSticky] = useState(true)
  const [isMobile, setIsMobile] = useState(false)

  useEffect(() => {
    const checkMobile = () => setIsMobile(window.innerWidth < 768)
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <SidebarContext.Provider
      value={{ isSidebarSticky, setIsSidebarSticky, isMobile }}
    >
      <div
        className="transition-all duration-300 ease-in-out"
        style={{
          marginLeft: isSidebarSticky && !isMobile ? '220px' : '0',
        }}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  )
}

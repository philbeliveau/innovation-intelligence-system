'use client'

import { createContext, useContext, useState, ReactNode } from 'react'

interface SidebarContextType {
  isSidebarSticky: boolean
  setIsSidebarSticky: (sticky: boolean) => void
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
  const [isSidebarSticky, setIsSidebarSticky] = useState(false)

  return (
    <SidebarContext.Provider value={{ isSidebarSticky, setIsSidebarSticky }}>
      <div
        className="transition-all duration-300 ease-in-out"
        style={{
          marginLeft: isSidebarSticky ? '220px' : '0',
        }}
      >
        {children}
      </div>
    </SidebarContext.Provider>
  )
}

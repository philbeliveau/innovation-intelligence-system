'use client'

import { useState } from 'react'
import Image from 'next/image'
import { X, Menu } from 'lucide-react'
import { getCardColorGradient } from '@/lib/card-colors'

export interface Spark {
  id: string
  title: string
  summary: string
  heroImageUrl?: string
  content: string
}

interface MobileSparkNavigationMenuProps {
  sparks: Spark[]
  selectedId: string
  onSelect: (id: string) => void
  onClose?: () => void
}

/**
 * Mobile hamburger menu for navigating between sparks on small screens
 * Shows a 2-column grid of spark thumbnails in a slide-in overlay
 */
export default function MobileSparkNavigationMenu({
  sparks,
  selectedId,
  onSelect,
  onClose,
}: MobileSparkNavigationMenuProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleSelectSpark = (id: string) => {
    onSelect(id)
    setIsOpen(false)
    onClose?.()
  }

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  return (
    <>
      {/* Hamburger Button - Fixed to top-left, only on mobile */}
      <button
        onClick={toggleMenu}
        className={`
          fixed top-4 left-4 z-50
          w-11 h-11
          bg-white rounded-lg shadow-lg
          flex items-center justify-center
          lg:hidden
          transition-transform duration-300
          ${isOpen ? 'rotate-90' : 'rotate-0'}
        `}
        aria-label="Toggle navigation menu"
        aria-expanded={isOpen}
      >
        {isOpen ? (
          <X className="w-6 h-6 text-gray-700" />
        ) : (
          <Menu className="w-6 h-6 text-gray-700" />
        )}
      </button>

      {/* Slide-in Menu Overlay */}
      <div
        className={`
          fixed inset-0 z-40 lg:hidden
          transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Backdrop - Blur and darken */}
        <div
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />

        {/* Menu Content - Slides in from left */}
        <div
          className="
            absolute left-0 top-0 h-full w-4/5
            bg-white shadow-xl overflow-y-auto
            safe-left safe-top safe-bottom
          "
        >
          {/* Header */}
          <div className="p-4 pt-16 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Sparks</h2>
            <p className="text-sm text-gray-500 mt-1">
              {sparks.length} innovation {sparks.length === 1 ? 'opportunity' : 'opportunities'}
            </p>
          </div>

          {/* Thumbnail Grid - 2 columns */}
          <div className="p-4">
            <div className="grid grid-cols-2 gap-2">
              {sparks.map((spark, index) => {
                const isSelected = spark.id === selectedId
                const gradientClass = getCardColorGradient(index + 1)

                return (
                  <button
                    key={spark.id}
                    onClick={() => handleSelectSpark(spark.id)}
                    className={`
                      relative aspect-video rounded-lg overflow-hidden
                      border-2 transition-all
                      ${isSelected ? 'border-[#5B9A99] ring-2 ring-[#5B9A99]/30' : 'border-gray-200'}
                      hover:border-[#5B9A99]/50
                      active:scale-95
                    `}
                    aria-label={`View spark ${index + 1}: ${spark.title}`}
                  >
                    {spark.heroImageUrl ? (
                      <Image
                        src={spark.heroImageUrl}
                        alt={spark.title}
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className={`w-full h-full bg-gradient-to-br ${gradientClass} flex items-center justify-center`}>
                        <span className="text-white/30 text-2xl font-bold">{index + 1}</span>
                      </div>
                    )}

                    {/* Number Badge */}
                    <div className="absolute top-2 left-2 w-6 h-6 bg-white rounded-full flex items-center justify-center text-xs font-bold shadow-md">
                      {index + 1}
                    </div>

                    {/* Selected Indicator */}
                    {isSelected && (
                      <div className="absolute inset-0 bg-[#5B9A99]/10 pointer-events-none" />
                    )}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

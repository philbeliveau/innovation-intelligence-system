'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'

const companyMapping: Record<string, string> = {
  lactalis: 'lactalis-canada',
  columbia: 'columbia-sportswear',
  decathlon: 'decathlon',
  mccormick: 'mccormick-usa',
}

export default function CompanyInput() {
  const router = useRouter()
  const [inputValue, setInputValue] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleValidation = async () => {
    // Clear previous error
    setError('')

    // Normalize input
    const normalized = inputValue.trim().toLowerCase()

    // Check if company exists in mapping
    const companyId = companyMapping[normalized]

    if (!companyId) {
      setError('Company not found. Please try: Lactalis, Columbia, Decathlon, or McCormick')
      return
    }

    // Call API to set company
    setIsLoading(true)

    try {
      const response = await fetch('/api/onboarding/set-company', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_id: companyId }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.error || 'Failed to load company profile')
        setIsLoading(false)
        return
      }

      // Success - redirect to upload page
      router.push('/upload')
    } catch {
      setError('Network error. Please try again.')
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleValidation()
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value)
    // Clear error on new input
    if (error) {
      setError('')
    }
  }

  const handleBlur = () => {
    if (inputValue.trim()) {
      handleValidation()
    }
  }

  return (
    <div className="w-full">
      <div className="relative">
        <Input
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onBlur={handleBlur}
          placeholder="your company URL"
          aria-label="Company name"
          disabled={isLoading}
          className="w-full h-10 px-4 text-center text-sm bg-white border border-gray-300 rounded-lg shadow-md placeholder:text-gray-400 focus:border-[#5B9A99] focus:outline-none focus:ring-2 focus:ring-[#5B9A99]/20 disabled:opacity-50 transition-all"
        />
        {isLoading && (
          <div className="absolute right-5 top-1/2 -translate-y-1/2">
            <div className="w-5 h-5 border-2 border-[#5B9A99] border-t-transparent rounded-full animate-spin" />
          </div>
        )}
      </div>

      {error && (
        <p className="mt-3 text-sm text-red-600 text-center" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}

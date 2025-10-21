import CompanyInput from '@/components/CompanyInput'
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs'

export default function Home() {
  // Perfect circular arrangement with gradually increasing sizes
  // 8 circles arranged in a circle, smallest to largest
  // Using 3-color teal palette: light (#7DB5AA), medium (#5B9A99), dark (#4A7F7E)
  const radius = 280 // Distance from center
  const baseSizes = [100, 115, 130, 145, 160, 175, 190, 205] // Gradually increasing, smaller average
  const colors = ['#7DB5AA', '#5B9A99', '#4A7F7E']

  const circles = baseSizes.map((size, index) => {
    const angle = (index * 360 / 8) - 90 // Start from top, distribute evenly (45° apart)
    const x = radius * Math.cos(angle * Math.PI / 180)
    const y = radius * Math.sin(angle * Math.PI / 180)

    return {
      x,
      y,
      size,
      color: colors[index % 3],
      opacity: 0.7 + (index * 0.02) // Gradually increase opacity
    }
  })

  return (
    <div className="min-h-screen bg-[#F5F5F5] relative overflow-hidden">
      {/* Decorative Teal Circles - Manual positioning to match target design */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none" aria-hidden="true">
        <div className="relative">
          {circles.map((circle, index) => (
            <div
              key={index}
              className="absolute rounded-full"
              style={{
                width: `${circle.size}px`,
                height: `${circle.size}px`,
                backgroundColor: circle.color,
                opacity: circle.opacity,
                left: `${circle.x}px`,
                top: `${circle.y}px`,
                transform: `translate(-50%, -50%)`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center justify-center min-h-screen relative z-10 px-4">
        {/* Title - Exact match to landing page */}
        <h1 className="text-5xl md:text-6xl font-bold mb-4 text-center text-gray-900">
          <span className="font-[family-name:var(--font-dancing-script)] text-[#5B9A99]">My</span> Board of Ideators
        </h1>

        {/* Subtitle - "Signals to Sparks" */}
        <p className="text-xl md:text-2xl italic text-[#5B9A99] mb-8">
          Signals to Sparks
        </p>

        {/* Authentication UI - Shows before company input */}
        <SignedOut>
          <div className="mb-8 text-center">
            <p className="text-gray-600 mb-4">Please sign in to continue</p>
            <SignInButton mode="modal">
              <button className="bg-[#5B9A99] hover:bg-[#4A7F7E] text-white font-semibold py-3 px-8 rounded-xl shadow-lg transition-all hover:shadow-xl">
                Sign In
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        {/* Company Input - Only shows when signed in */}
        <SignedIn>
          {/* Company Input Component */}
          <CompanyInput />
        </SignedIn>
      </div>
    </div>
  )
}

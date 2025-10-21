import CompanyInput from '@/components/CompanyInput'
import { SignedIn, SignedOut, SignInButton, UserButton } from '@clerk/nextjs'

export default function Home() {
  // Circular arrangement shifted left-up with gradually increasing sizes
  // 8 circles arranged in a circle, smallest to largest
  // Using 3-color teal palette: light (#7DB5AA), medium (#5B9A99), dark (#4A7F7E)
  const radius = 310 // Slightly larger radius for better spread
  const baseSizes = [100, 115, 130, 145, 160, 175, 190, 205] // Gradually increasing
  const colors = ['#7DB5AA', '#5B9A99', '#4A7F7E']

  const circles = baseSizes.map((size, index) => {
    // Incomplete circle - 270° arc starting from top, leaving gap on right side
    // Distribute 8 circles across 270° (not full 360°)
    const arcSpan = 270 // degrees of arc coverage
    const angle = 30 + (index * arcSpan / (baseSizes.length - 1)) // Start at 30°, spread across 270°
    const x = radius * Math.cos(angle * Math.PI / 180)
    const y = radius * Math.sin(angle * Math.PI / 180)

    return {
      x,
      y,
      size,
      color: colors[index % 3],
      opacity: 0.4 + (index * 0.075) // Gradually increase opacity: smallest = 0.4, largest = 0.925
    }
  })

  return (
    <div className="min-h-screen bg-[#F5F5F5] relative overflow-hidden">
      {/* Decorative Teal Circles - Centered to match target design */}
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        {/* Container centered */}
        <div className="absolute left-[50%] top-[50%]">
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
      </div>

      {/* Main Content - centered */}
      <div className="flex flex-col items-center justify-center min-h-screen relative z-10 px-4">
        <div className="flex flex-col items-center gap-3">
          {/* Light gray circle behind title */}
          <div className="absolute w-[400px] h-[400px] bg-white/60 rounded-full -z-10 left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2" aria-hidden="true"></div>

          {/* Title - Exact match to landing page */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 relative">
            <span className="font-[family-name:var(--font-dancing-script)] text-[#5B9A99]">My</span> Board of Ideators
          </h1>

          {/* Subtitle - "Signals to Sparks" - offset to the right */}
          <p className="text-base md:text-lg italic text-[#5B9A99] self-end pr-8">
            Signals to Sparks
          </p>

          {/* Authentication UI - Shows before company input */}
          <SignedOut>
            <div className="mt-2 text-center self-end pr-8">
              <p className="text-gray-600 mb-3 text-sm">Please sign in to continue</p>
              <SignInButton mode="modal">
                <button className="bg-[#5B9A99] hover:bg-[#4A7F7E] text-white font-semibold py-2 px-6 rounded-xl shadow-lg transition-all hover:shadow-xl text-sm">
                  Sign In
                </button>
              </SignInButton>
            </div>
          </SignedOut>

          {/* Company Input - Only shows when signed in */}
          <SignedIn>
            {/* Company Input Component */}
            <div className="w-64 self-end pr-8">
              <CompanyInput />
            </div>
          </SignedIn>
        </div>
      </div>
    </div>
  )
}

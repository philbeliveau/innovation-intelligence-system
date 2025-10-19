import { ReactNode } from 'react'

interface OnboardingHeroProps {
  children: ReactNode
}

export default function OnboardingHero({ children }: OnboardingHeroProps) {
  // 8 circles: 2 teal, 2 blue, 2 yellow, 2 orange
  // Positioned in circular arrangement (clock positions)
  // Top: teal (12 o'clock)
  // Upper-right: yellow (2 o'clock)
  // Right: orange (3 o'clock)
  // Lower-right: blue (5 o'clock)
  // Bottom: teal (6 o'clock)
  // Lower-left: yellow (7 o'clock)
  // Left: orange (9 o'clock)
  // Upper-left: blue (10 o'clock)

  const radius = 280 // Distance from center
  const circleSize = 120 // Circle diameter

  // Evenly spaced circles (360 / 8 = 45 degrees apart)
  const circles = [
    { color: 'bg-teal-600', angle: 0 },     // 12 o'clock
    { color: 'bg-blue-600', angle: 45 },    // 1:30
    { color: 'bg-yellow-500', angle: 90 },  // 3 o'clock
    { color: 'bg-orange-600', angle: 135 }, // 4:30
    { color: 'bg-teal-600', angle: 180 },   // 6 o'clock
    { color: 'bg-blue-600', angle: 225 },   // 7:30
    { color: 'bg-yellow-500', angle: 270 }, // 9 o'clock
    { color: 'bg-orange-600', angle: 315 }, // 10:30
  ]

  return (
    <div className="relative w-full max-w-4xl mx-auto px-8">
      {/* Circular arrangement of colored circles */}
      <div className="relative w-[700px] h-[700px] mx-auto">
        {circles.map((circle, index) => {
          // Calculate position using trigonometry
          // Angle in radians (subtract 90 to start at top)
          const angleRad = ((circle.angle - 90) * Math.PI) / 180
          const x = radius * Math.cos(angleRad)
          const y = radius * Math.sin(angleRad)

          return (
            <div
              key={index}
              className={`absolute w-[${circleSize}px] h-[${circleSize}px] rounded-full ${circle.color}`}
              style={{
                width: `${circleSize}px`,
                height: `${circleSize}px`,
                left: `calc(50% + ${x}px - ${circleSize / 2}px)`,
                top: `calc(50% + ${y}px - ${circleSize / 2}px)`,
              }}
              aria-hidden="true"
            />
          )
        })}

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <h1 className="text-4xl font-normal mb-8 text-center">
            <span className="text-teal-600 italic font-serif">My</span>{' '}
            <span className="text-gray-900">Board of Ideators</span>
          </h1>

          {/* Input component passed as children */}
          {children}
        </div>
      </div>
    </div>
  )
}

/**
 * Color palette for opportunity card placeholder images
 * Uses vibrant gradients to create visually distinct cards
 */

export const CARD_COLOR_GRADIENTS = [
  // Teal to Cyan (brand colors)
  'from-[#5B9A99] to-[#4FC3C8]',
  // Purple to Pink
  'from-purple-500 to-pink-500',
  // Orange to Red
  'from-orange-400 to-red-500',
  // Blue to Indigo
  'from-blue-400 to-indigo-600',
  // Green to Teal
  'from-green-400 to-teal-500',
  // Yellow to Orange
  'from-yellow-400 to-orange-500',
  // Pink to Rose
  'from-pink-400 to-rose-500',
  // Indigo to Purple
  'from-indigo-400 to-purple-600',
  // Cyan to Blue
  'from-cyan-400 to-blue-500',
  // Lime to Green
  'from-lime-400 to-green-500',
]

/**
 * Get a deterministic color gradient for a card based on its number
 * @param cardNumber - The sequential number of the card (1-based)
 * @returns Tailwind gradient classes
 */
export function getCardColorGradient(cardNumber: number): string {
  const index = (cardNumber - 1) % CARD_COLOR_GRADIENTS.length
  return CARD_COLOR_GRADIENTS[index]
}

/**
 * Get solid background color for overlays/badges
 * @param cardNumber - The sequential number of the card (1-based)
 * @returns Tailwind background color class
 */
export function getCardColorSolid(cardNumber: number): string {
  const solidColors = [
    'bg-[#5B9A99]',
    'bg-purple-500',
    'bg-orange-400',
    'bg-blue-400',
    'bg-green-400',
    'bg-yellow-400',
    'bg-pink-400',
    'bg-indigo-400',
    'bg-cyan-400',
    'bg-lime-400',
  ]
  const index = (cardNumber - 1) % solidColors.length
  return solidColors[index]
}

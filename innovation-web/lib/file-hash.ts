// Innovation Intelligence System - File Hashing Utility
// Client-side file hashing using Web Crypto API for duplicate detection

/**
 * Calculate SHA-256 hash of a file's content
 * @param file - File object to hash
 * @returns Promise<string> - Hex string representation of the hash
 * @throws Error if Web Crypto API is not available or hashing fails
 */
export async function calculateFileHash(file: File): Promise<string> {
  // Check if Web Crypto API is available
  if (!crypto || !crypto.subtle) {
    throw new Error('Web Crypto API not available in this browser')
  }

  try {
    // Read file as ArrayBuffer
    const arrayBuffer = await file.arrayBuffer()

    // Calculate SHA-256 hash
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer)

    // Convert ArrayBuffer to hex string
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray
      .map((byte) => byte.toString(16).padStart(2, '0'))
      .join('')

    return hashHex
  } catch (error) {
    console.error('File hashing failed:', error)
    throw new Error('Failed to calculate file hash')
  }
}

/**
 * Calculate SHA-256 hash with progress tracking for large files
 * @param file - File object to hash
 * @param onProgress - Optional callback for progress updates (0-100)
 * @returns Promise<string> - Hex string representation of the hash
 */
export async function calculateFileHashWithProgress(
  file: File,
  onProgress?: (progress: number) => void
): Promise<string> {
  // Check if Web Crypto API is available
  if (!crypto || !crypto.subtle) {
    throw new Error('Web Crypto API not available in this browser')
  }

  try {
    const chunkSize = 1024 * 1024 // 1MB chunks
    const chunks = Math.ceil(file.size / chunkSize)

    // For small files (< 5MB), use simple approach
    if (file.size < 5 * 1024 * 1024) {
      if (onProgress) onProgress(50)
      const hash = await calculateFileHash(file)
      if (onProgress) onProgress(100)
      return hash
    }

    // For large files, read in chunks and update progress
    const fileReader = new FileReader()
    let currentChunk = 0
    const arrayBuffers: ArrayBuffer[] = []

    // Read file in chunks
    while (currentChunk < chunks) {
      const start = currentChunk * chunkSize
      const end = Math.min(start + chunkSize, file.size)
      const blob = file.slice(start, end)

      const buffer = await new Promise<ArrayBuffer>((resolve, reject) => {
        fileReader.onload = (e) => {
          if (e.target?.result instanceof ArrayBuffer) {
            resolve(e.target.result)
          } else {
            reject(new Error('Failed to read file chunk'))
          }
        }
        fileReader.onerror = () => reject(fileReader.error)
        fileReader.readAsArrayBuffer(blob)
      })

      arrayBuffers.push(buffer)
      currentChunk++

      // Report progress (80% for reading, 20% for hashing)
      if (onProgress) {
        onProgress(Math.floor((currentChunk / chunks) * 80))
      }
    }

    // Concatenate all chunks
    const totalLength = arrayBuffers.reduce((acc, buf) => acc + buf.byteLength, 0)
    const combined = new Uint8Array(totalLength)
    let offset = 0
    for (const buffer of arrayBuffers) {
      combined.set(new Uint8Array(buffer), offset)
      offset += buffer.byteLength
    }

    if (onProgress) onProgress(90)

    // Calculate hash
    const hashBuffer = await crypto.subtle.digest('SHA-256', combined)

    // Convert to hex string
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    const hashHex = hashArray
      .map((byte) => byte.toString(16).padStart(2, '0'))
      .join('')

    if (onProgress) onProgress(100)

    return hashHex
  } catch (error) {
    console.error('File hashing with progress failed:', error)
    throw new Error('Failed to calculate file hash')
  }
}

/**
 * Check if browser supports Web Crypto API for file hashing
 * @returns boolean - true if supported
 */
export function isFileHashingSupported(): boolean {
  return typeof crypto !== 'undefined' && typeof crypto.subtle !== 'undefined'
}

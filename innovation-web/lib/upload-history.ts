// Innovation Intelligence System - Upload History Management
// LocalStorage utility functions for managing upload history

export interface UploadMetadata {
  upload_id: string
  filename: string
  uploaded_at: number // Unix timestamp
  blob_url: string
  company_id: string
  content_hash?: string // SHA-256 hash of file content for duplicate detection
}

const MAX_UPLOADS_PER_COMPANY = 20

/**
 * Get upload history for a specific company from localStorage
 * @param companyId - The company identifier
 * @returns Array of upload metadata objects (empty array if none found)
 */
export function getUploadHistory(companyId: string): UploadMetadata[] {
  try {
    const key = `upload_history_${companyId}`
    const data = localStorage.getItem(key)
    if (!data) return []

    const history = JSON.parse(data) as UploadMetadata[]

    // Validate structure and filter invalid entries
    return history.filter(upload =>
      upload.upload_id &&
      upload.filename &&
      upload.uploaded_at &&
      upload.blob_url &&
      upload.company_id === companyId
    )
  } catch (error) {
    console.error('Failed to read upload history:', error)
    // Clear corrupted data
    try {
      const key = `upload_history_${companyId}`
      localStorage.removeItem(key)
    } catch {
      // Ignore cleanup errors
    }
    return []
  }
}

/**
 * Add a new upload to the history for a specific company
 * Enforces FIFO 20-upload limit
 * @param companyId - The company identifier
 * @param upload - The upload metadata to add
 */
export function addUploadToHistory(
  companyId: string,
  upload: UploadMetadata
): void {
  try {
    const history = getUploadHistory(companyId)

    // Add to beginning (most recent first)
    history.unshift(upload)

    // Enforce 20-upload limit (FIFO - remove oldest)
    if (history.length > MAX_UPLOADS_PER_COMPANY) {
      history.splice(MAX_UPLOADS_PER_COMPANY)
    }

    const key = `upload_history_${companyId}`
    localStorage.setItem(key, JSON.stringify(history))
  } catch (error) {
    console.error('Failed to save upload history:', error)
    // Check if it's a quota error
    if (error instanceof DOMException && (
      error.name === 'QuotaExceededError' ||
      error.name === 'NS_ERROR_DOM_QUOTA_REACHED'
    )) {
      console.warn('LocalStorage quota exceeded - upload history feature disabled')
    }
    // Gracefully degrade - don't block upload flow
  }
}

/**
 * Remove a specific upload from the history
 * Also deletes from database if content_hash is available
 * @param companyId - The company identifier
 * @param uploadId - The upload ID to remove
 */
export async function removeUploadFromHistory(
  companyId: string,
  uploadId: string
): Promise<void> {
  try {
    const history = getUploadHistory(companyId)

    // Find the upload to get content_hash for database deletion
    const uploadToDelete = history.find(u => u.upload_id === uploadId)

    // Remove from localStorage
    const filtered = history.filter(u => u.upload_id !== uploadId)
    const key = `upload_history_${companyId}`
    localStorage.setItem(key, JSON.stringify(filtered))

    // Delete from database if content_hash exists
    if (uploadToDelete?.content_hash) {
      try {
        const response = await fetch(`/api/document/by-hash/${uploadToDelete.content_hash}`, {
          method: 'DELETE',
        })

        if (!response.ok) {
          console.warn('Failed to delete document from database:', response.status)
        }
      } catch (error) {
        console.error('Failed to delete document from database:', error)
        // Don't throw - localStorage deletion was successful
      }
    }
  } catch (error) {
    console.error('Failed to remove from upload history:', error)
  }
}

/**
 * Clear all upload history for a specific company
 * @param companyId - The company identifier
 */
export function clearUploadHistory(companyId: string): void {
  try {
    const key = `upload_history_${companyId}`
    localStorage.removeItem(key)
  } catch (error) {
    console.error('Failed to clear upload history:', error)
  }
}

/**
 * Check if localStorage is available and writable
 * @returns true if localStorage is available
 */
export function isLocalStorageAvailable(): boolean {
  try {
    const test = '__localStorage_test__'
    localStorage.setItem(test, test)
    localStorage.removeItem(test)
    return true
  } catch {
    return false
  }
}

/**
 * Check if a file with the same content hash has already been uploaded
 * @param companyId - The company identifier
 * @param contentHash - The SHA-256 hash of the file content
 * @returns UploadMetadata if duplicate found, null otherwise
 */
export function findDuplicateUpload(
  companyId: string,
  contentHash: string
): UploadMetadata | null {
  if (!contentHash) return null

  try {
    const history = getUploadHistory(companyId)

    // Find upload with matching content hash
    const duplicate = history.find(
      (upload) => upload.content_hash === contentHash
    )

    return duplicate || null
  } catch (error) {
    console.error('Failed to check for duplicate upload:', error)
    return null
  }
}

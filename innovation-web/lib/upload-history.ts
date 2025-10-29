// Innovation Intelligence System - Upload History Management
// LocalStorage utility functions for managing upload history

export interface UploadMetadata {
  upload_id: string
  filename: string
  uploaded_at: number // Unix timestamp
  blob_url: string
  company_id: string // Kept for backward compatibility, but no longer used for filtering
  content_hash?: string // SHA-256 hash of file content for duplicate detection
}

const MAX_UPLOADS_PER_USER = 20
const STORAGE_KEY = 'upload_history' // Single key for all user uploads

/**
 * Get upload history for the user from localStorage
 * Now returns ALL uploads regardless of company (company_id is deprecated)
 * @param _companyId - Deprecated, kept for API compatibility
 * @returns Array of upload metadata objects (empty array if none found)
 */
export function getUploadHistory(_companyId?: string): UploadMetadata[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY)
    if (!data) return []

    const history = JSON.parse(data) as UploadMetadata[]

    // Validate structure and filter invalid entries
    return history.filter(upload =>
      upload.upload_id &&
      upload.filename &&
      upload.uploaded_at &&
      upload.blob_url
    )
  } catch (error) {
    console.error('Failed to read upload history:', error)
    // Clear corrupted data
    try {
      localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Ignore cleanup errors
    }
    return []
  }
}

/**
 * Add a new upload to the history
 * Enforces FIFO 20-upload limit per user (not per company)
 * @param _companyId - Deprecated, kept for API compatibility
 * @param upload - The upload metadata to add
 */
export function addUploadToHistory(
  _companyId: string,
  upload: UploadMetadata
): void {
  try {
    const history = getUploadHistory()

    // Add to beginning (most recent first)
    history.unshift(upload)

    // Enforce 20-upload limit (FIFO - remove oldest)
    if (history.length > MAX_UPLOADS_PER_USER) {
      history.splice(MAX_UPLOADS_PER_USER)
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
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
 * @param _companyId - Deprecated, kept for API compatibility
 * @param uploadId - The upload ID to remove
 */
export async function removeUploadFromHistory(
  _companyId: string,
  uploadId: string
): Promise<void> {
  try {
    const history = getUploadHistory()

    // Find the upload to get content_hash for database deletion
    const uploadToDelete = history.find(u => u.upload_id === uploadId)
    console.log('[removeUploadFromHistory] Upload to delete:', uploadToDelete)

    // Remove from localStorage
    const filtered = history.filter(u => u.upload_id !== uploadId)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
    console.log('[removeUploadFromHistory] Removed from localStorage')

    // Delete from database if content_hash exists
    if (uploadToDelete?.content_hash) {
      console.log('[removeUploadFromHistory] Deleting from database, hash:', uploadToDelete.content_hash)
      try {
        const response = await fetch(`/api/document/by-hash/${uploadToDelete.content_hash}`, {
          method: 'DELETE',
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          console.warn('[removeUploadFromHistory] Failed to delete from database:', response.status, errorData)
        } else {
          const result = await response.json()
          console.log('[removeUploadFromHistory] Successfully deleted from database:', result)
        }
      } catch (error) {
        console.error('[removeUploadFromHistory] Error deleting from database:', error)
        // Don't throw - localStorage deletion was successful
      }
    } else {
      console.warn('[removeUploadFromHistory] No content_hash available, skipping database deletion')
    }
  } catch (error) {
    console.error('Failed to remove from upload history:', error)
  }
}

/**
 * Clear all upload history for the user
 * @param _companyId - Deprecated, kept for API compatibility
 */
export function clearUploadHistory(_companyId?: string): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
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
 * @param _companyId - Deprecated, kept for API compatibility
 * @param contentHash - The SHA-256 hash of the file content
 * @returns UploadMetadata if duplicate found, null otherwise
 */
export function findDuplicateUpload(
  _companyId: string,
  contentHash: string
): UploadMetadata | null {
  if (!contentHash) return null

  try {
    const history = getUploadHistory()

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

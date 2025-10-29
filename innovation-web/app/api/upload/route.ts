import { put, type PutBlobResult } from '@vercel/blob';
import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';

const ALLOWED_TYPES = ['application/pdf', 'text/plain', 'text/markdown'];
const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB in bytes
const MAX_RETRY_ATTEMPTS = 3;

/**
 * Sanitize filename to prevent path traversal attacks
 * @param filename - Original filename from user
 * @returns Sanitized filename safe for storage paths
 */
function sanitizeFilename(filename: string): string {
  // Remove path separators and parent directory references
  return filename.replace(/[\/\\\.\.]/g, '_').replace(/_{2,}/g, '_');
}

/**
 * Exponential backoff delay for retry logic
 * @param attempt - Current attempt number (0-indexed)
 * @returns Delay in milliseconds
 */
function getRetryDelay(attempt: number): number {
  return Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
}

/**
 * Upload file to Vercel Blob with retry logic
 * @param path - Upload path in blob storage
 * @param file - File to upload
 * @returns Blob object with URL
 */
async function uploadWithRetry(path: string, file: File): Promise<PutBlobResult> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt < MAX_RETRY_ATTEMPTS; attempt++) {
    try {
      const blob = await put(path, file, { access: 'public' });
      return blob;
    } catch (error) {
      lastError = error as Error;
      console.error(`Upload attempt ${attempt + 1} failed:`, error);

      // If this isn't the last attempt, wait before retrying
      if (attempt < MAX_RETRY_ATTEMPTS - 1) {
        const delay = getRetryDelay(attempt);
        console.log(`Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  // All attempts failed - throw error matching AC23 spec
  throw lastError || new Error('Upload failed');
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    // Check authentication
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      );
    }

    // Extract file and content hash from form data
    const formData = await request.formData();
    const fileEntry = formData.get('file');
    const contentHash = formData.get('content_hash') as string | null;

    // Validate file exists and is a File object
    if (!fileEntry) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    if (!(fileEntry instanceof File)) {
      return NextResponse.json(
        { error: 'Invalid file format' },
        { status: 400 }
      );
    }

    const file = fileEntry;

    // Validate file type
    if (!ALLOWED_TYPES.includes(file.type)) {
      return NextResponse.json(
        { error: 'Invalid file type' },
        { status: 400 }
      );
    }

    // Validate file size (before upload)
    if (file.size > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: 'File too large (max 25MB)' },
        { status: 400 }
      );
    }

    // Check for Blob token
    if (!process.env.BLOB_READ_WRITE_TOKEN) {
      console.error('BLOB_READ_WRITE_TOKEN not configured');
      return NextResponse.json(
        { error: 'Upload failed' },
        { status: 500 }
      );
    }

    // Generate upload path with sanitized filename
    const timestamp = Date.now();
    const sanitizedName = sanitizeFilename(file.name);
    const uploadPath = `uploads/${timestamp}-${sanitizedName}`;

    // Upload to Blob with retry logic
    let blob;
    try {
      blob = await uploadWithRetry(uploadPath, file);
    } catch (error) {
      console.error('Blob upload failed after retries:', error);
      return NextResponse.json(
        { error: 'Upload failed' },
        { status: 500 }
      );
    }

    // Generate upload ID
    const uploadId = `upload-${timestamp}`;

    // Save document to database
    try {
      // Find or create Prisma user from Clerk userId
      const user = await prisma.user.upsert({
        where: { clerkId: userId },
        update: {},
        create: {
          clerkId: userId,
          email: '', // Email can be populated from Clerk user object if needed
        }
      });

      // Create document record with content hash
      await prisma.document.create({
        data: {
          userId: user.id,
          fileName: file.name,
          fileSize: file.size,
          blobUrl: blob.url,
          contentHash: contentHash || null,
          uploadedAt: new Date(),
        }
      });
    } catch (dbError) {
      // Log database error but don't fail the upload
      // The file is already in blob storage, so we return success
      console.error('Database persistence error:', dbError);
    }

    // Create response object
    const response = {
      upload_id: uploadId,
      blob_url: blob.url,
      file_name: file.name,
      file_size: file.size,
      uploaded_at: new Date().toISOString()
    };

    return NextResponse.json(response, { status: 200 });

  } catch (error) {
    // Handle unexpected errors
    console.error('Upload error:', error);

    // Check if it's a timeout or network error
    if (error instanceof Error && (
      error.message.includes('timeout') ||
      error.message.includes('network')
    )) {
      return NextResponse.json(
        { error: 'Upload timeout' },
        { status: 500 }
      );
    }

    // Generic server error
    return NextResponse.json(
      { error: 'Upload failed' },
      { status: 500 }
    );
  }
}

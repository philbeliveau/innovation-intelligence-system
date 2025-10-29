import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';

/**
 * DELETE /api/document/by-hash/[contentHash]
 * Delete a document from the database by content hash
 */
export async function DELETE(
  request: Request,
  props: { params: Promise<{ contentHash: string }> }
): Promise<NextResponse> {
  const params = await props.params;
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      );
    }

    // Find Prisma user from Clerk userId
    const user = await prisma.user.findUnique({
      where: { clerkId: userId },
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Delete all documents with this content hash for this user
    // Uses unique constraint: @@unique([userId, contentHash])
    const result = await prisma.document.deleteMany({
      where: {
        userId: user.id,
        contentHash: params.contentHash,
      },
    });

    if (result.count === 0) {
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }

    return NextResponse.json(
      { message: 'Document deleted successfully', count: result.count },
      { status: 200 }
    );
  } catch (error) {
    console.error('Document deletion error:', error);
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}

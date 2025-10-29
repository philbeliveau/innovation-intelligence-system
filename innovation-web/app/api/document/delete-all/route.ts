import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';

/**
 * DELETE /api/document/delete-all
 * Delete ALL documents for the current user (for debugging)
 */
export async function DELETE(): Promise<NextResponse> {
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

    // Delete all documents for this user
    const result = await prisma.document.deleteMany({
      where: {
        userId: user.id,
      },
    });

    return NextResponse.json(
      { message: 'All documents deleted', count: result.count },
      { status: 200 }
    );
  } catch (error) {
    console.error('Document deletion error:', error);
    return NextResponse.json(
      { error: 'Failed to delete documents' },
      { status: 500 }
    );
  }
}

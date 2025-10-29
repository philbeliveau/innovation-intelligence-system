import { NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';
import { prisma } from '@/lib/prisma';

/**
 * DELETE /api/document/[documentId]
 * Delete a document from the database
 */
export async function DELETE(
  request: Request,
  { params }: { params: { documentId: string } }
): Promise<NextResponse> {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized - Please sign in to continue' },
        { status: 401 }
      );
    }

    // Find or create Prisma user from Clerk userId
    const user = await prisma.user.findUnique({
      where: { clerkId: userId },
    });

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Find the document and verify ownership
    const document = await prisma.document.findFirst({
      where: {
        id: params.documentId,
        userId: user.id,
      },
    });

    if (!document) {
      return NextResponse.json(
        { error: 'Document not found or access denied' },
        { status: 404 }
      );
    }

    // Delete the document from database
    await prisma.document.delete({
      where: { id: params.documentId },
    });

    return NextResponse.json(
      { message: 'Document deleted successfully' },
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

import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'
import { prisma } from '@/lib/prisma'

/**
 * POST /api/cards/[cardId]/star - Toggle star/favorite status for an opportunity card
 */
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ cardId: string }> }
) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const { cardId } = await params

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { clerkId: userId },
    })

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      )
    }

    // Fetch card with run relation to verify ownership
    const card = await prisma.opportunityCard.findUnique({
      where: { id: cardId },
      include: { run: true },
    })

    if (!card || card.run.userId !== user.id) {
      return NextResponse.json(
        { error: 'Card not found or access denied' },
        { status: 404 }
      )
    }

    // Toggle starred status
    const updatedCard = await prisma.opportunityCard.update({
      where: { id: cardId },
      data: { isStarred: !card.isStarred },
    })

    return NextResponse.json({
      id: updatedCard.id,
      isStarred: updatedCard.isStarred,
      message: 'Card starred status updated',
    })
  } catch (error) {
    console.error('[API /cards/:id/star POST] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

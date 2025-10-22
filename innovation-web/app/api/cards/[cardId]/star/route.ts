import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'

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

    // TODO: Replace with actual Prisma query
    // const card = await prisma.opportunityCard.findUnique({
    //   where: { id: cardId },
    //   include: { run: true }
    // })
    //
    // if (!card || card.run.userId !== userId) {
    //   return NextResponse.json(
    //     { error: 'Card not found or access denied' },
    //     { status: 404 }
    //   )
    // }
    //
    // const updatedCard = await prisma.opportunityCard.update({
    //   where: { id: cardId },
    //   data: { isStarred: !card.isStarred }
    // })

    // Mock response for development
    return NextResponse.json({
      id: cardId,
      isStarred: true, // In real implementation, toggle the current value
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

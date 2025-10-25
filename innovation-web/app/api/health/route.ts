import { NextResponse } from 'next/server'

/**
 * GET /api/health
 *
 * Health check endpoint for backend connectivity testing
 * Returns 200 OK if frontend is running and Prisma is accessible
 */
export async function GET() {
  try {
    // Test Prisma connectivity
    const { prisma } = await import('@/lib/prisma')

    // Quick query to verify database connection
    await prisma.$queryRaw`SELECT 1`

    return NextResponse.json({
      status: 'ok',
      timestamp: new Date().toISOString(),
      prisma: 'connected'
    })
  } catch (error) {
    console.error('[API /health] Health check failed:', error)

    return NextResponse.json(
      {
        status: 'degraded',
        timestamp: new Date().toISOString(),
        prisma: 'disconnected',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    )
  }
}

const { PrismaClient } = require('@prisma/client')
const prisma = new PrismaClient()

async function main() {
  const runs = await prisma.pipelineRun.findMany({
    orderBy: { createdAt: 'desc' },
    take: 10,
    include: {
      user: { select: { email: true, clerkId: true } },
      _count: { select: { opportunityCards: true } }
    }
  })
  console.log(JSON.stringify({ count: runs.length, runs }, null, 2))
}

main()
  .catch(e => console.error(JSON.stringify({ error: e.message }, null, 2)))
  .finally(() => prisma.$disconnect())

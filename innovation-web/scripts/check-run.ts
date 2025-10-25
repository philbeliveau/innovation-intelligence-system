import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()
const runId = process.argv[2] || 'run-1761426324-9533'

async function checkRun() {
  const run = await prisma.pipelineRun.findUnique({
    where: { id: runId },
    include: {
      stageOutputs: { orderBy: { stageNumber: 'asc' } },
      opportunityCards: true,
      inspirationReport: true
    }
  })

  if (!run) {
    console.log(`❌ Run ${runId} not found in database yet`)
    await prisma.$disconnect()
    return
  }

  console.log(`✅ Run found: ${run.id}`)
  console.log(`   Status: ${run.status}`)
  console.log(`   Stages: ${run.stageOutputs.length}/5`)
  console.log(`   Cards: ${run.opportunityCards.length}`)
  console.log(`   Report: ${run.inspirationReport ? 'YES' : 'NO'}`)

  if (run.stageOutputs.length > 0) {
    const latest = run.stageOutputs[run.stageOutputs.length - 1]
    console.log(`   Latest Stage: ${latest.stageNumber} - ${latest.status}`)
  }

  await prisma.$disconnect()
}

checkRun().catch(console.error)

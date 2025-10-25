import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

const runId = process.argv[2] || 'run-1761426324-9533'

async function monitor() {
  console.log(`Monitoring pipeline: ${runId}\n`)

  const interval = setInterval(async () => {
    try {
      const run = await prisma.pipelineRun.findUnique({
        where: { id: runId },
        include: {
          stageOutputs: {
            orderBy: { stageNumber: 'asc' }
          },
          opportunityCards: true,
          inspirationReport: true
        }
      })

      if (!run) {
        console.log('⏳ Waiting for run to appear in database...')
        return
      }

      console.log(`\n📊 Run: ${run.id}`)
      console.log(`   Status: ${run.status}`)
      console.log(`   Stages: ${run.stageOutputs.length}/5`)

      if (run.stageOutputs.length > 0) {
        const latest = run.stageOutputs[run.stageOutputs.length - 1]
        console.log(`   Latest: Stage ${latest.stageNumber} - ${latest.status}`)
      }

      console.log(`   Opportunity Cards: ${run.opportunityCards.length}`)
      console.log(`   Inspiration Report: ${run.inspirationReport ? 'YES' : 'NO'}`)

      if (run.status === 'COMPLETED') {
        console.log('\n✅ Pipeline COMPLETED!')
        console.log(`\n🎯 Final Results:`)
        console.log(`   - Opportunity Cards: ${run.opportunityCards.length}`)
        console.log(`   - Inspiration Report: ${run.inspirationReport ? 'Created' : 'Missing'}`)

        if (run.opportunityCards.length > 0) {
          console.log(`\n📋 Opportunity Cards:`)
          run.opportunityCards.forEach(card => {
            console.log(`   ${card.number}. ${card.title}`)
          })
        }

        clearInterval(interval)
        await prisma.$disconnect()
        process.exit(0)
      }

      if (run.status === 'FAILED') {
        console.log('\n❌ Pipeline FAILED!')
        clearInterval(interval)
        await prisma.$disconnect()
        process.exit(1)
      }
    } catch (error) {
      console.error('Error monitoring pipeline:', error)
    }
  }, 5000) // Poll every 5 seconds
}

monitor().catch(console.error)

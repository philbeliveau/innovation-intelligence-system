import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function checkOpportunities() {
  const runId = 'run-1761419288183-501'

  console.log(`\n🔍 Checking run: ${runId}\n`)

  // Get the run
  const run = await prisma.pipelineRun.findUnique({
    where: { id: runId },
    include: {
      opportunityCards: true,
      inspirationReport: true,
      stageOutputs: {
        orderBy: { stageNumber: 'asc' }
      }
    }
  })

  if (!run) {
    console.log('❌ Run not found in database')
    process.exit(1)
  }

  console.log('✅ Run found:')
  console.log(`   Status: ${run.status}`)
  console.log(`   Created: ${run.createdAt}`)
  console.log(`   Completed: ${run.completedAt}`)
  console.log(`   Duration: ${run.duration}ms`)
  console.log(`   Company: ${run.companyName}`)
  console.log(`   Document: ${run.documentName}`)

  console.log(`\n📊 Stage Outputs: ${run.stageOutputs.length}`)
  for (const stage of run.stageOutputs) {
    console.log(`   Stage ${stage.stageNumber}: ${stage.status}`)
  }

  console.log(`\n🎯 Opportunity Cards: ${run.opportunityCards.length}`)
  if (run.opportunityCards.length === 0) {
    console.log('   ⚠️  No opportunity cards found!')
  } else {
    for (const card of run.opportunityCards) {
      console.log(`   ${card.number}. ${card.title}`)
      console.log(`      Content length: ${card.content.length} chars`)
    }
  }

  console.log(`\n📄 Inspiration Report: ${run.inspirationReport ? 'YES' : 'NO'}`)
  if (run.inspirationReport) {
    console.log(`   Selected Track: ${run.inspirationReport.selectedTrack}`)
    console.log(`   Non-Selected Track: ${run.inspirationReport.nonSelectedTrack}`)
  }

  // Check Stage 5 output for opportunities
  const stage5 = run.stageOutputs.find(s => s.stageNumber === 5)
  if (stage5) {
    console.log(`\n🔬 Analyzing Stage 5 output...`)
    try {
      const stage5Data = JSON.parse(stage5.output)
      const opportunities = stage5Data.opportunities || []
      console.log(`   Opportunities in Stage 5 JSON: ${opportunities.length}`)
      if (opportunities.length > 0) {
        console.log(`   First opportunity structure:`)
        console.log(`   - title: ${opportunities[0].title ? 'YES' : 'MISSING'}`)
        console.log(`   - markdown: ${opportunities[0].markdown ? 'YES' : 'MISSING'}`)
        console.log(`   - content: ${opportunities[0].content ? 'YES' : 'MISSING'}`)
      }
    } catch (e) {
      console.log(`   ❌ Failed to parse Stage 5 output as JSON`)
    }
  }

  await prisma.$disconnect()
}

checkOpportunities().catch(console.error)

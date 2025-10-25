import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function testWebhook() {
  const runId = 'run-1761419288183-501'

  // Get Stage 5 output
  const stage5 = await prisma.stageOutput.findFirst({
    where: {
      runId,
      stageNumber: 5
    }
  })

  if (!stage5) {
    console.log('Stage 5 not found')
    process.exit(1)
  }

  const stage5Data = JSON.parse(stage5.output)
  const opportunities = stage5Data.opportunities || []

  console.log(`Found ${opportunities.length} opportunities in Stage 5 output`)
  console.log('\nFirst opportunity structure:')
  console.log(JSON.stringify(opportunities[0], null, 2))

  // Build webhook payload
  const webhookPayload = {
    status: "COMPLETED",
    completedAt: new Date().toISOString(),
    duration: 180000,
    opportunities: opportunities,
    stageOutputs: {
      stage1: {},
      stage2: {},
      stage3: {},
      stage4: {},
      stage5: stage5Data
    }
  }

  console.log('\n📤 Webhook payload ready')
  console.log(`   Opportunities: ${opportunities.length}`)
  console.log(`   First title: ${opportunities[0]?.title}`)
  console.log(`   Has markdown: ${!!opportunities[0]?.markdown}`)

  // Test with curl command
  const curlCommand = `curl -X POST "https://innovation-web-rho.vercel.app/api/pipeline/${runId}/complete" \\
  -H "Content-Type: application/json" \\
  -H "X-Webhook-Secret: YOUR_SECRET_HERE" \\
  -d '${JSON.stringify(webhookPayload)}'`

  console.log('\n📋 Test webhook with:')
  console.log(curlCommand)

  await prisma.$disconnect()
}

testWebhook().catch(console.error)

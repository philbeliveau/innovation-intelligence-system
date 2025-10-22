import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Starting database seed...')

  // Create test user with mock Clerk ID
  const testUser = await prisma.user.upsert({
    where: { clerkId: 'user_test_seed_123456' },
    update: {},
    create: {
      clerkId: 'user_test_seed_123456',
      email: 'test@example.com',
      name: 'Test User',
    },
  })

  console.log('✅ Created test user:', testUser.email)

  // Create test pipeline run
  const testRun = await prisma.pipelineRun.create({
    data: {
      userId: testUser.id,
      documentName: 'Test Innovation Report 2024.pdf',
      documentUrl: 'https://example.com/test-report.pdf',
      companyName: 'Lactalis Canada',
      status: 'COMPLETED',
      pipelineVersion: 'v1.0.0',
      duration: 45000, // 45 seconds
      completedAt: new Date(),
    },
  })

  console.log('✅ Created test pipeline run:', testRun.id)

  // Create test opportunity cards
  const cards = await Promise.all([
    prisma.opportunityCard.create({
      data: {
        runId: testRun.id,
        number: 1,
        title: 'Premium Protein Cheese Line',
        content: `## Premium Protein Cheese Line

**Opportunity:** Launch a high-protein artisan cheese line targeting health-conscious millennials

**Market Insight:** Plant-based alternatives growing but dairy protein still preferred by 67% of consumers

**Mechanism:** Better-For-You-ification + Premiumization

**Retail Viability:**
- Price: $8.99/8oz
- Target velocity: 12 units/store/week
- Margin: 38%
- Launch timeline: 8 months`,
        isStarred: true,
      },
    }),
    prisma.opportunityCard.create({
      data: {
        runId: testRun.id,
        number: 2,
        title: 'Snackable Cheese Bites',
        content: `## Snackable Cheese Bites

**Opportunity:** Single-serve protein snack packs for on-the-go consumption

**Market Insight:** Grab-and-go protein snacks category growing at 15% CAGR

**Mechanism:** Convenience Shift + Format Migration

**Retail Viability:**
- Price: $2.49/pack
- Target velocity: 24 units/store/week
- Margin: 42%
- Launch timeline: 6 months`,
        isStarred: false,
      },
    }),
    prisma.opportunityCard.create({
      data: {
        runId: testRun.id,
        number: 3,
        title: 'Artisan Cheese Discovery Box',
        content: `## Artisan Cheese Discovery Box

**Opportunity:** Monthly subscription box featuring regional artisan cheeses

**Market Insight:** Subscription boxes for gourmet foods growing 22% YoY

**Mechanism:** Premiumization + Occasion Expansion

**Retail Viability:**
- Price: $39.99/month
- Target velocity: DTC only
- Margin: 55%
- Launch timeline: 10 months`,
        isStarred: false,
      },
    }),
  ])

  console.log(`✅ Created ${cards.length} test opportunity cards`)

  // Create test stage outputs
  const stages = [
    {
      stageNumber: 1,
      stageName: 'Mechanism Extraction',
      status: 'COMPLETED' as const,
      output: 'Extracted 5 innovation mechanisms from input document...',
      completedAt: new Date(Date.now() - 40000),
    },
    {
      stageNumber: 2,
      stageName: 'Innovation Anatomy',
      status: 'COMPLETED' as const,
      output: 'Mapped innovations to Doblin\'s 10 Types framework...',
      completedAt: new Date(Date.now() - 30000),
    },
    {
      stageNumber: 3,
      stageName: 'Jobs Architecture',
      status: 'COMPLETED' as const,
      output: 'Identified functional, emotional, and social jobs...',
      completedAt: new Date(Date.now() - 20000),
    },
    {
      stageNumber: 4,
      stageName: 'CPG Translation',
      status: 'COMPLETED' as const,
      output: 'Applied 5 CPG patterns with retail viability gates...',
      completedAt: new Date(Date.now() - 10000),
    },
    {
      stageNumber: 5,
      stageName: 'Retail-Ready Cards',
      status: 'COMPLETED' as const,
      output: 'Generated 3 retail-ready opportunity cards...',
      completedAt: new Date(),
    },
  ]

  for (const stage of stages) {
    await prisma.stageOutput.create({
      data: {
        ...stage,
        runId: testRun.id,
      },
    })
  }

  console.log(`✅ Created ${stages.length} test stage outputs`)

  // Create test inspiration report
  await prisma.inspirationReport.create({
    data: {
      runId: testRun.id,
      selectedTrack: 'Premium Protein Cheese Line - Selected for development',
      nonSelectedTrack: 'Other opportunities archived for future consideration',
      stage1Output: 'Detailed mechanism extraction output...',
      stage2Output: 'Detailed innovation anatomy output...',
      stage3Output: 'Detailed jobs architecture output...',
      stage4Output: 'Detailed CPG translation output...',
      stage5Output: 'Detailed retail-ready cards output...',
    },
  })

  console.log('✅ Created test inspiration report')

  console.log('\n🎉 Database seeded successfully!')
}

main()
  .then(async () => {
    await prisma.$disconnect()
  })
  .catch(async (e) => {
    console.error('❌ Seed failed:', e)
    await prisma.$disconnect()
    process.exit(1)
  })

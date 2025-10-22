import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@clerk/nextjs/server'

/**
 * GET /api/runs/[runId] - Get specific run details with all relations
 */
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const { runId } = await params

    // TODO: Replace with actual Prisma query
    // const run = await prisma.pipelineRun.findUnique({
    //   where: { id: runId, userId },
    //   include: {
    //     opportunityCards: { orderBy: { number: 'asc' } },
    //     inspirationReport: true,
    //     stageOutputs: { orderBy: { stageNumber: 'asc' } }
    //   }
    // })

    // Mock data for development
    const mockRun = {
      id: runId,
      documentName: 'CPG Innovation Trends 2024.pdf',
      companyName: 'Lactalis Canada',
      status: 'COMPLETED',
      createdAt: new Date(Date.now() - 3600000).toISOString(),
      completedAt: new Date(Date.now() - 1800000).toISOString(),
      duration: 1800,
      pipelineVersion: '2.1.0',
      opportunityCards: [
        {
          id: `card-1-${runId}`,
          number: 1,
          title: 'Protein-Enriched Cheese Snack Bites',
          content: `## Opportunity Overview
**Mechanism:** Better-for-you-ification + Format Migration

Transform traditional cheese portions into high-protein, grab-and-go snack bites targeting active consumers and parents.

## Target Consumer
- Health-conscious adults (25-45)
- Parents seeking nutritious kids' snacks
- Gym-goers and active lifestyle consumers

## Key Innovation
- 12g protein per serving
- Shelf-stable packaging
- Single-serve portions (30g)

## Retail Metrics
- Price Point: $4.99 for 5-pack
- Target Margin: 38%
- Launch Timeline: 9 months`,
          isStarred: false,
        },
        {
          id: `card-2-${runId}`,
          number: 2,
          title: 'Artisan Cheese Discovery Subscription Box',
          content: `## Opportunity Overview
**Mechanism:** Subscription model + Premiumization

Monthly curated selection of premium artisan cheeses with tasting notes and pairing suggestions.

## Target Consumer
- Food enthusiasts and entertaining hosts
- Premium cheese consumers (current Président buyers)
- Gift market opportunity

## Key Innovation
- Expert curation and education
- Exclusive small-batch cheeses
- Recipe cards and wine pairing guide

## Retail Metrics
- Price Point: $39.99/month
- Target Margin: 42%
- Launch Timeline: 6 months`,
          isStarred: true,
        },
        {
          id: `card-3-${runId}`,
          number: 3,
          title: 'Ready-to-Eat Cheese & Charcuterie Trays',
          content: `## Opportunity Overview
**Mechanism:** Convenience shift + Occasion expansion

Pre-assembled, refrigerated entertainment trays for impulse purchase and immediate consumption.

## Target Consumer
- Last-minute entertainers
- Small gatherings (2-4 people)
- Busy professionals

## Key Innovation
- 72-hour shelf life
- Aesthetically presented (Instagram-worthy)
- Multiple price tiers ($12.99, $19.99, $29.99)

## Retail Metrics
- Target Margin: 35%
- Launch Timeline: 12 months
- Velocity: 8-12 units/store/week`,
          isStarred: false,
        },
        {
          id: `card-4-${runId}`,
          number: 4,
          title: 'Spreadable Cheese Dessert Line',
          content: `## Opportunity Overview
**Mechanism:** Occasion expansion + Format migration

Sweet spreadable cheese products positioned as healthier dessert alternatives.

## Target Consumer
- Health-conscious dessert lovers
- Parents seeking better alternatives
- Morning routine consumers

## Key Innovation
- Honey, berry, and chocolate flavors
- 30% less sugar than cream cheese frosting
- Pairs with fruit, crackers, or toast

## Retail Metrics
- Price Point: $5.49 (200g tub)
- Target Margin: 40%
- Launch Timeline: 10 months`,
          isStarred: false,
        },
        {
          id: `card-5-${runId}`,
          number: 5,
          title: 'B2B Office Snack Program',
          content: `## Opportunity Overview
**Mechanism:** Channel innovation + Subscription model

Bulk cheese snack delivery program for corporate offices and coworking spaces.

## Target Consumer
- Office managers and HR departments
- Coworking space operators
- Corporate wellness programs

## Key Innovation
- Customizable variety packs
- Monthly delivery
- Branded mini-fridges (for large accounts)

## Retail Metrics
- Price Point: $299/month (serves 50 employees)
- Target Margin: 45%
- Launch Timeline: 8 months`,
          isStarred: true,
        },
      ],
      inspirationReport: {
        id: `report-${runId}`,
        selectedTrack: `# Selected Innovation Track: Health & Convenience

## Key Mechanisms Identified
1. **Better-for-you-ification** - Adding protein, reducing fat
2. **Convenience shift** - Ready-to-eat formats
3. **Format migration** - Traditional cheese → portable snacks

## Consumer Insights
The modern consumer wants traditional quality in modern formats. They value:
- Transparency in ingredients
- Convenience without compromise
- Health benefits that don't sacrifice taste

## Competitive Landscape
Traditional cheese brands are slow to innovate. Opportunity exists to capture the "better snacking" trend before mass-market players arrive.`,
        nonSelectedTrack: `# Alternative Track: Premium Positioning

## Key Mechanisms Identified
1. **Premiumization** - Craft story, higher price points
2. **Education & Experience** - Cheese as discovery
3. **Gift & Entertainment** - Occasion expansion

## Consumer Insights
Premium consumers seek authenticity and experience. They want to be seen as sophisticated and knowledgeable about food.

## Competitive Landscape
Import brands dominate premium, but domestic premium opportunity exists with storytelling around local partnerships.`,
        stage1Output: `# Stage 1: Mechanism Extraction

## Mechanisms Identified from Source Material

### Mechanism 1: Subscription Eliminates Replenishment Friction
- **Pattern:** Recurring need creates effort burden
- **Solution:** Automated delivery removes decision fatigue
- **Constraint Eliminated:** Time (45 min shopping → 0 min)
- **Transferable to:** Any consumable product with predictable usage

### Mechanism 2: Better-for-You-ification
- **Pattern:** Category seen as indulgent gets health upgrade
- **Solution:** Add protein, remove/reduce negative attributes
- **Constraint Eliminated:** Guilt (traditional snack → justified snack)
- **Transferable to:** Any "treat" category

### Mechanism 3: Format Migration
- **Pattern:** Traditional format limits occasions
- **Solution:** New format unlocks new consumption moments
- **Constraint Eliminated:** Context limitations
- **Transferable to:** Established categories ripe for reinvention`,
        stage2Output: `# Stage 2: Innovation Anatomy (Doblin's 10 Types)

## Mechanism 1 Analysis
**Types Activated:**
1. Profit Model (subscription revenue)
2. Service (automated fulfillment)
3. Channel (direct-to-consumer)

**Defensibility:** MEDIUM (2-3 types)

## Mechanism 2 Analysis
**Types Activated:**
1. Product Performance (functional improvement)
2. Brand (health positioning)

**Defensibility:** LOW (1-2 types, easily copied)

## Mechanism 3 Analysis
**Types Activated:**
1. Product System (new formats)
2. Customer Engagement (new occasions)
3. Channel (new distribution)

**Defensibility:** MEDIUM-HIGH (3 types)`,
        stage3Output: `# Stage 3: Jobs-to-be-Done Architecture

## Job 1: "I need a healthy snack that doesn't feel like a compromise"
**Functional:** Satisfy hunger between meals
**Emotional:** Feel good about my choices
**Social:** Be seen as health-conscious
**Constraint:** Current snacks are either healthy OR tasty, not both

## Job 2: "I need to impress guests without spending hours preparing"
**Functional:** Provide quality food for entertaining
**Emotional:** Feel confident as a host
**Social:** Be perceived as sophisticated
**Constraint:** Time (traditional prep takes 30+ min)

## Job 3: "I need to keep my office team happy without vending machines"
**Functional:** Provide quality snacks to employees
**Emotional:** Show care for team wellbeing
**Social:** Be seen as a progressive employer
**Constraint:** Management overhead (ordering, stocking)`,
        stage4Output: `# Stage 4: CPG Translation

## Application to Lactalis Portfolio

### Pattern 1: Better-for-You-ification
**Brand Fit:** President's Cheese → President's Fuel
- Add 12g protein per serving
- Reduce fat by 30%
- Clean label (5 ingredients)
**Retail Viability:** ✓ Walmart accepted, 38% margin, <12 mo

### Pattern 2: Premiumization
**Brand Fit:** President's Reserve Collection
- Artisan small-batch story
- 2x price point vs. standard
- Expert curation angle
**Retail Viability:** ✓ Target/Whole Foods, 42% margin, 6 mo

### Pattern 3: Convenience Shift
**Brand Fit:** President's Entertaining Solutions
- Pre-assembled trays
- Impulse purchase positioning
- Multiple price tiers
**Retail Viability:** ✓ All channels, 35% margin, 12 mo`,
        stage5Output: `# Stage 5: Retail-Ready Opportunity Cards

[See Opportunity Cards tab for full details]

## 30-Second Buyer Pitch Examples

**Card 1:** "Protein cheese bites that compete in the $2B better-for-you snacking category. $4.99 5-pack, 38% margin, 9-month launch."

**Card 2:** "$39.99 monthly cheese subscription targeting the 12M food enthusiast households. DTC revenue, 42% margin, 6-month launch."

**Card 3:** "Ready-to-eat charcuterie trays capturing impulse entertainment purchases. $12.99-$29.99 range, 35% margin, targets 8-12 units/store/week."`,
      },
      stageOutputs: [
        {
          id: `stage-1-${runId}`,
          stageNumber: 1,
          stageName: 'Mechanism Extraction',
          status: 'COMPLETED',
          completedAt: new Date(Date.now() - 3240000).toISOString(),
          output: JSON.stringify({
            mechanisms: [
              {
                type: 'subscription_friction_removal',
                description: 'Eliminate replenishment effort through automation',
              },
              {
                type: 'better_for_you',
                description: 'Add health attributes to indulgent categories',
              },
            ],
          }),
        },
        {
          id: `stage-2-${runId}`,
          stageNumber: 2,
          stageName: 'Innovation Anatomy',
          status: 'COMPLETED',
          completedAt: new Date(Date.now() - 2880000).toISOString(),
          output: JSON.stringify({
            doblin_types: ['Product Performance', 'Service', 'Channel', 'Brand'],
            defensibility: 'MEDIUM',
          }),
        },
        {
          id: `stage-3-${runId}`,
          stageNumber: 3,
          stageName: 'Jobs-to-be-Done',
          status: 'COMPLETED',
          completedAt: new Date(Date.now() - 2520000).toISOString(),
          output: JSON.stringify({
            jobs: [
              {
                functional: 'Satisfy hunger between meals',
                emotional: 'Feel good about choices',
                social: 'Be seen as health-conscious',
              },
            ],
          }),
        },
        {
          id: `stage-4-${runId}`,
          stageNumber: 4,
          stageName: 'CPG Translation',
          status: 'COMPLETED',
          completedAt: new Date(Date.now() - 2160000).toISOString(),
          output: JSON.stringify({
            patterns: ['Better-for-you-ification', 'Premiumization', 'Convenience Shift'],
            retail_viability: true,
          }),
        },
        {
          id: `stage-5-${runId}`,
          stageNumber: 5,
          stageName: 'Retail-Ready Cards',
          status: 'COMPLETED',
          completedAt: new Date(Date.now() - 1800000).toISOString(),
          output: JSON.stringify({
            cards_generated: 5,
            avg_margin: 40,
            avg_launch_timeline: 9,
          }),
        },
      ],
    }

    return NextResponse.json(mockRun)
  } catch (error) {
    console.error('[API /runs/:id GET] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

/**
 * DELETE /api/runs/[runId] - Delete a pipeline run
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ runId: string }> }
) {
  try {
    const { userId } = await auth()

    if (!userId) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      )
    }

    const { runId } = await params

    // Delete from Vercel Blob storage
    // Find blobs matching the runId pattern
    try {
      // In a real implementation, you would:
      // 1. Query database for blob URLs associated with this runId
      // 2. Delete each blob from Vercel Blob storage
      // 3. Delete database records

      // For now, we'll attempt to delete based on naming convention
      // This is a placeholder implementation

      console.log(`[API /runs/:id DELETE] Deleting run ${runId}`)

      // Return success even if blob doesn't exist
      return NextResponse.json({
        success: true,
        message: 'Run deleted successfully',
      })
    } catch (blobError) {
      console.error('[API /runs/:id DELETE] Blob deletion error:', blobError)
      // Continue even if blob deletion fails
    }

    return NextResponse.json({
      success: true,
      message: 'Run deleted successfully',
    })
  } catch (error) {
    console.error('[API /runs/:id DELETE] Error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

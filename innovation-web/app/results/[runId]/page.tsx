import { cookies } from 'next/headers'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import OpportunityCard from '@/components/OpportunityCard'
import Link from 'next/link'
import { prisma } from '@/lib/prisma'

interface PageProps {
  params: Promise<{ runId: string }>
}

interface Opportunity {
  number: number
  title: string
  markdown: string
}

async function loadOpportunities(runId: string): Promise<Opportunity[]> {
  try {
    // Query Prisma database directly (Server Component advantage)
    const run = await prisma.pipelineRun.findUnique({
      where: { id: runId },
      include: {
        stageOutputs: {
          where: { stageNumber: 5 },
          orderBy: { stageNumber: 'asc' }
        }
      }
    })

    if (!run) {
      console.error(`Pipeline run not found: ${runId}`)
      return []
    }

    // Check if Stage 5 is completed
    const stage5 = run.stageOutputs[0]
    if (!stage5 || stage5.status !== 'COMPLETED') {
      console.warn('Stage 5 not completed yet')
      return []
    }

    // Parse Stage 5 output
    let stage5Output: Record<string, unknown>
    try {
      stage5Output = JSON.parse(stage5.output)
    } catch {
      console.error('Failed to parse Stage 5 output as JSON')
      return []
    }

    const opportunitiesData = (stage5Output.opportunities as Record<string, unknown>[]) || []

    // Transform backend format to frontend format
    return opportunitiesData.map((opp: Record<string, unknown>, index: number) => ({
      number: index + 1,
      title: (opp.title as string) || `Opportunity ${index + 1}`,
      markdown: (opp.markdown as string) || (opp.content as string) || ''
    }))
  } catch (error) {
    console.error('Error loading opportunities:', error)
    return []
  }
}

async function getCompanyName(): Promise<string | null> {
  try {
    const cookieStore = await cookies()
    const companyId = cookieStore.get('company_id')?.value

    if (!companyId) {
      return null
    }

    // Simple mapping of company IDs to names (avoid filesystem access in Next.js)
    const companyNames: Record<string, string> = {
      'lactalis-canada': 'Lactalis Canada',
      'general-mills': 'General Mills',
      'nestle': 'Nestlé',
      // Add more as needed
    }

    return companyNames[companyId] || companyId
  } catch (error) {
    console.warn('Could not fetch company name:', error)
    return null
  }
}

export default async function ResultsPage({ params }: PageProps) {
  const { runId } = await params

  // Load opportunities
  const opportunities = await loadOpportunities(runId)

  // Get company name
  const companyName = await getCompanyName()

  // If no opportunities found at all, show error
  if (opportunities.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="p-8 max-w-md w-full text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Opportunities Found</h2>
          <p className="text-gray-600 mb-6">
            Pipeline completed but no opportunities were generated. Please try again or contact support.
          </p>
          <Link href="/upload">
            <Button className="w-full">Return to Upload</Button>
          </Link>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-amber-50">
      {/* Header - Mobile responsive with flex-wrap */}
      <div className="bg-white border-b-[3px] md:border-b-[5px] border-black">
        <div className="container mx-auto px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between flex-wrap gap-2 sm:gap-4">
            <div className="flex items-center gap-2 sm:gap-4">
              <Link href="/upload">
                <button className="bg-black text-white px-3 py-1.5 sm:px-4 sm:py-2 font-bold uppercase text-xs sm:text-sm border-2 border-black shadow-[3px_3px_0_#000] sm:shadow-[4px_4px_0_#000] hover:shadow-[4px_4px_0_#000] sm:hover:shadow-[6px_6px_0_#000] hover:translate-x-[-1px] hover:translate-y-[-1px] sm:hover:translate-x-[-2px] sm:hover:translate-y-[-2px] transition-all">
                  ← Back
                </button>
              </Link>
              <h1 className="text-lg sm:text-xl md:text-2xl font-black uppercase text-black">Innovation Opportunities</h1>
            </div>
            {companyName && (
              <span className="bg-gray-700 text-white px-2 py-0.5 sm:px-3 sm:py-1 font-bold uppercase text-xs border-2 border-black">
                {companyName}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Warning Banner (if some files are missing) - Responsive borders */}
      {opportunities.length < 5 && (
        <div className="container mx-auto px-4 pt-4 sm:pt-6">
          <div className="bg-yellow-200 border-[3px] md:border-4 border-black p-3 sm:p-4 shadow-[3px_3px_0_#000] sm:shadow-[4px_4px_0_#000]">
            <p className="text-black font-bold text-sm sm:text-base">
              ⚠️ Warning: Only {opportunities.length} of 5 opportunities are available. Some files may be missing.
            </p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-6 sm:py-8">
        {/* Action Buttons - Stack on mobile, side-by-side on desktop */}
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6 sm:mb-8">
          <Link href="/upload" className="w-full sm:w-auto">
            <button className="w-full sm:w-auto bg-orange-500 text-white px-4 py-2.5 sm:px-6 sm:py-3 font-black uppercase text-base sm:text-lg border-[3px] sm:border-4 border-black shadow-[4px_4px_0_#000] sm:shadow-[6px_6px_0_#000] hover:shadow-[6px_6px_0_#000] sm:hover:shadow-[8px_8px_0_#000] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all">
              🚀 New Pipeline
            </button>
          </Link>
          <button
            disabled
            title="PDF export coming in Phase 2"
            className="w-full sm:w-auto bg-gray-300 text-gray-600 px-4 py-2.5 sm:px-6 sm:py-3 font-black uppercase text-base sm:text-lg border-[3px] sm:border-4 border-black shadow-[4px_4px_0_#000] sm:shadow-[6px_6px_0_#000] cursor-not-allowed opacity-50"
          >
            📄 Download PDF
          </button>
        </div>

        {/* Opportunity Cards - Responsive grid: 1 col mobile, 2 col tablet, 3 col desktop */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 justify-items-center max-w-6xl mx-auto">
          {opportunities.map((opp) => (
            <OpportunityCard
              key={opp.number}
              number={opp.number}
              title={opp.title}
              markdown={opp.markdown}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

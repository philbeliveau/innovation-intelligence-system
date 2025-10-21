import { cookies } from 'next/headers'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import OpportunityCard from '@/components/OpportunityCard'
import Link from 'next/link'

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
    // Fetch status from backend API to get opportunities
    const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${BACKEND_URL}/status/${runId}`, {
      cache: 'no-store'
    })

    if (!response.ok) {
      console.error(`Failed to fetch status for ${runId}: ${response.status}`)
      return []
    }

    const status = await response.json()

    // Extract opportunities from Stage 5 output
    const stage5 = status.stages?.['5']
    if (!stage5 || stage5.status !== 'complete') {
      console.warn('Stage 5 not completed yet')
      return []
    }

    const opportunitiesData = stage5.output?.opportunities || []

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
    const companyId = cookieStore.get('companyId')?.value

    if (!companyId) {
      return null
    }

    // Read brand profile directly to get name
    const yaml = await import('yaml')
    const { readFile: readBrandFile } = await import('fs/promises')

    const brandPath = `../data/brand-profiles/${companyId}.yaml`
    const brandContent = await readBrandFile(brandPath, 'utf-8')
    const brandData = yaml.parse(brandContent)

    return brandData.name || companyId
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
      {/* Header */}
      <div className="bg-white border-b-[5px] border-black">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/upload">
                <button className="bg-black text-white px-4 py-2 font-bold uppercase text-sm border-2 border-black shadow-[4px_4px_0_#000] hover:shadow-[6px_6px_0_#000] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all">
                  ← Back
                </button>
              </Link>
              <h1 className="text-2xl font-black uppercase text-black">Innovation Opportunities</h1>
            </div>
            {companyName && (
              <span className="bg-gray-700 text-white px-3 py-1 font-bold uppercase text-xs border-2 border-black">
                {companyName}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Success Banner */}
      <div className="bg-white border-b-[5px] border-black">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4 bg-gradient-to-r from-green-200 to-green-400 p-4 border-4 border-black shadow-[6px_6px_0_#000]">
            <div className="text-4xl font-black">✓</div>
            <div>
              <h2 className="text-xl font-black uppercase text-black">Pipeline Complete</h2>
              <p className="text-black font-bold">
                {opportunities.length} {opportunities.length === 1 ? 'Opportunity' : 'Opportunities'} Generated Successfully
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Warning Banner (if some files are missing) */}
      {opportunities.length < 5 && (
        <div className="container mx-auto px-4 pt-6">
          <div className="bg-yellow-200 border-4 border-black p-4 shadow-[4px_4px_0_#000]">
            <p className="text-black font-bold">
              ⚠️ Warning: Only {opportunities.length} of 5 opportunities are available. Some files may be missing.
            </p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Link href="/upload">
            <button className="bg-orange-500 text-white px-6 py-3 font-black uppercase text-lg border-4 border-black shadow-[6px_6px_0_#000] hover:shadow-[8px_8px_0_#000] hover:translate-x-[-2px] hover:translate-y-[-2px] transition-all">
              🚀 New Pipeline
            </button>
          </Link>
          <button
            disabled
            title="PDF export coming in Phase 2"
            className="bg-gray-300 text-gray-600 px-6 py-3 font-black uppercase text-lg border-4 border-black shadow-[6px_6px_0_#000] cursor-not-allowed opacity-50"
          >
            📄 Download PDF
          </button>
        </div>

        {/* Opportunity Cards */}
        <div className="flex flex-wrap gap-6 justify-center max-w-6xl mx-auto">
          {opportunities.map((opp) => (
            <OpportunityCard
              key={opp.number}
              number={opp.number}
              title={opp.title}
              markdown={opp.markdown}
            />
          ))}
        </div>

        {/* Footer Action Buttons */}
        <div className="max-w-4xl mx-auto mt-8 flex flex-wrap gap-4 justify-center">
          <Link href="/upload">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              🚀 Start New Pipeline
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}

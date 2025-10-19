import { readFile } from 'fs/promises'
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
  const outputDir = `data/test-outputs/${runId}/stage5`
  const opportunities: Opportunity[] = []

  // Try to read all 5 opportunity files
  for (let num = 1; num <= 5; num++) {
    try {
      const filePath = `${outputDir}/opportunity-${num}.md`
      const markdown = await readFile(filePath, 'utf-8')

      // Extract title from first heading (# Title)
      const titleMatch = markdown.match(/^#\s+(.+)$/m)
      const title = titleMatch ? titleMatch[1] : `Opportunity ${num}`

      opportunities.push({ number: num, title, markdown })
    } catch (error) {
      // File doesn't exist or can't be read - skip it
      console.warn(`Could not read opportunity file ${num}:`, error)
    }
  }

  return opportunities
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/upload">
                <Button variant="outline" className="flex items-center gap-2">
                  ← Back
                </Button>
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">Innovation Opportunities</h1>
            </div>
            {companyName && (
              <Badge variant="secondary" className="text-sm">
                {companyName}
              </Badge>
            )}
          </div>
        </div>
      </div>

      {/* Success Banner */}
      <div className="bg-green-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="text-3xl">✓</div>
            <div>
              <h2 className="text-xl font-bold">Pipeline Complete</h2>
              <p className="text-green-100">
                {opportunities.length} {opportunities.length === 1 ? 'Opportunity' : 'Opportunities'} Generated Successfully
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Warning Banner (if some files are missing) */}
      {opportunities.length < 5 && (
        <div className="container mx-auto px-4 pt-6">
          <Alert className="bg-yellow-50 border-yellow-200">
            <AlertDescription className="text-yellow-800">
              ⚠️ Warning: Only {opportunities.length} of 5 opportunities are available. Some files may be missing.
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Link href="/upload">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
              🚀 New Pipeline
            </Button>
          </Link>
          <Button
            size="lg"
            variant="outline"
            disabled
            title="PDF export coming in Phase 2"
            className="cursor-not-allowed opacity-50"
          >
            📄 Download PDF
          </Button>
        </div>

        {/* Opportunity Cards */}
        <div className="max-w-4xl mx-auto">
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

'use client'

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'

interface InspirationReport {
  id: string
  selectedTrack: string
  nonSelectedTrack: string
  stage1Output: string
  stage2Output: string
  stage3Output: string
  stage4Output: string
  stage5Output: string
}

interface RunDetailFullReportProps {
  report: InspirationReport
}

/**
 * Format stage output - handles both markdown strings and legacy JSON
 */
function formatStageOutput(output: string): string {
  if (!output || output.trim() === '') {
    return '*No output available for this stage*'
  }

  // If it's already markdown (doesn't start with '{' or '['), return as-is
  const trimmed = output.trim()
  if (!trimmed.startsWith('{') && !trimmed.startsWith('[')) {
    return output
  }

  // Legacy handling: Try to parse as JSON (for old data)
  try {
    const data = JSON.parse(output)

    // Pretty print the JSON as fallback
    return '```json\n' + JSON.stringify(data, null, 2) + '\n```'
  } catch {
    // If parsing fails, it's probably already markdown
    return output
  }
}

export default function RunDetailFullReport({ report }: RunDetailFullReportProps) {
  const stages = [
    {
      number: 1,
      name: 'Mechanism Extraction',
      output: report.stage1Output,
      description: 'Extracting transferable innovation mechanisms from source material',
    },
    {
      number: 2,
      name: 'Innovation Anatomy',
      output: report.stage2Output,
      description: "Mapping innovations to Doblin's 10 Types framework",
    },
    {
      number: 3,
      name: 'Jobs-to-be-Done Architecture',
      output: report.stage3Output,
      description: 'Understanding functional, emotional, and social jobs being addressed',
    },
    {
      number: 4,
      name: 'CPG Translation',
      output: report.stage4Output,
      description: 'Applying mechanisms to CPG-specific patterns and retail viability',
    },
    {
      number: 5,
      name: 'Retail-Ready Opportunities',
      output: report.stage5Output,
      description: 'Generating buyer-ready concepts with metrics',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Ideation Tracks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Selected Track */}
        <Card className="border-4 border-[#5B9A99]">
          <CardHeader className="bg-teal-100 border-b-4 border-[#5B9A99]">
            <CardTitle className="text-xl font-black text-[#5B9A99]">
              Selected Track ✓
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeSanitize]}
              >
                {report.selectedTrack}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>

        {/* Non-Selected Track */}
        <Card className="border-4 border-[#5B9A99]">
          <CardHeader className="bg-gray-100 border-b-4 border-[#5B9A99]">
            <CardTitle className="text-xl font-black text-gray-700">
              Alternative Track
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeSanitize]}
              >
                {report.nonSelectedTrack}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Stage Outputs */}
      <Card className="border-4 border-[#5B9A99]">
        <CardHeader className="bg-teal-100 border-b-4 border-[#5B9A99]">
          <CardTitle className="text-2xl font-black text-[#5B9A99]">
            Pipeline Stage Outputs
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Accordion type="single" collapsible className="w-full">
            {stages.map((stage) => (
              <AccordionItem key={stage.number} value={`stage-${stage.number}`}>
                <AccordionTrigger className="px-6 py-4 hover:bg-teal-50 border-b-2 border-[#5B9A99]">
                  <div className="flex items-start gap-4 text-left">
                    <div className="shrink-0 w-8 h-8 rounded-full bg-[#5B9A99] text-white flex items-center justify-center font-bold">
                      {stage.number}
                    </div>
                    <div>
                      <div className="font-black text-lg text-[#5B9A99]">{stage.name}</div>
                      <div className="text-sm text-gray-600 font-normal">
                        {stage.description}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-6 py-6 bg-teal-50">
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeSanitize]}
                    >
                      {formatStageOutput(stage.output)}
                    </ReactMarkdown>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  )
}

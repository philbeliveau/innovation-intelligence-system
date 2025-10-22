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
        <Card className="border-4 border-black">
          <CardHeader className="bg-green-100 border-b-4 border-black">
            <CardTitle className="text-xl font-black">
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
        <Card className="border-4 border-black">
          <CardHeader className="bg-gray-100 border-b-4 border-black">
            <CardTitle className="text-xl font-black">
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
      <Card className="border-4 border-black">
        <CardHeader className="bg-blue-100 border-b-4 border-black">
          <CardTitle className="text-2xl font-black">
            Pipeline Stage Outputs
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Accordion type="single" collapsible className="w-full">
            {stages.map((stage) => (
              <AccordionItem key={stage.number} value={`stage-${stage.number}`}>
                <AccordionTrigger className="px-6 py-4 hover:bg-gray-50 border-b-2 border-black">
                  <div className="flex items-start gap-4 text-left">
                    <div className="shrink-0 w-8 h-8 rounded-full bg-black text-white flex items-center justify-center font-bold">
                      {stage.number}
                    </div>
                    <div>
                      <div className="font-black text-lg">{stage.name}</div>
                      <div className="text-sm text-gray-600 font-normal">
                        {stage.description}
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-6 py-6 bg-gray-50">
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeSanitize]}
                    >
                      {stage.output || '*No output available for this stage*'}
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

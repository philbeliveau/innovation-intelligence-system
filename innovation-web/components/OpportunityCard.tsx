import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface OpportunityCardProps {
  number: number
  title: string
  markdown: string
}

export default function OpportunityCard({ number, title, markdown }: OpportunityCardProps) {
  return (
    <Card className="mb-6 overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 pb-4">
        <div className="flex items-center gap-3">
          <Badge className="bg-blue-600 hover:bg-blue-700 text-white">
            Opportunity #{number}
          </Badge>
          <h2 className="text-xl font-bold text-gray-900">{title}</h2>
        </div>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700 prose-strong:text-gray-900 prose-ul:text-gray-700 prose-ol:text-gray-700">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              // Prevent dangerous elements (XSS protection)
              script: () => null,
              iframe: () => null,
              object: () => null,
              embed: () => null,
              // Style headings
              h1: ({ ...props }) => <h1 className="text-2xl font-bold mt-6 mb-4" {...props} />,
              h2: ({ ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3" {...props} />,
              h3: ({ ...props }) => <h3 className="text-lg font-semibold mt-4 mb-2" {...props} />,
              // Style lists
              ul: ({ ...props }) => <ul className="list-disc list-inside space-y-1 my-3" {...props} />,
              ol: ({ ...props }) => <ol className="list-decimal list-inside space-y-1 my-3" {...props} />,
              // Handle overflow for long content
              pre: ({ ...props }) => (
                <pre className="overflow-x-auto bg-gray-50 p-4 rounded-md my-4" {...props} />
              ),
              table: ({ ...props }) => (
                <div className="overflow-x-auto my-4">
                  <table className="min-w-full divide-y divide-gray-300" {...props} />
                </div>
              ),
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      </CardContent>
    </Card>
  )
}

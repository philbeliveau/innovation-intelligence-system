'use client'

import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronUp, CheckCircle2, XCircle, Loader2 } from 'lucide-react'

interface StageOutput {
  id: string
  stageNumber: number
  stageName: string
  status: 'COMPLETED' | 'FAILED' | 'PROCESSING'
  output: string
  completedAt: string | null
}

interface RunDetailPipelineStagesProps {
  stages: StageOutput[]
}

export default function RunDetailPipelineStages({ stages }: RunDetailPipelineStagesProps) {
  const [expandedStages, setExpandedStages] = useState<Set<number>>(new Set())

  const toggleStage = (stageNumber: number) => {
    setExpandedStages((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(stageNumber)) {
        newSet.delete(stageNumber)
      } else {
        newSet.add(stageNumber)
      }
      return newSet
    })
  }

  const getStatusIcon = (status: StageOutput['status']) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle2 className="w-6 h-6 text-green-500" />
      case 'FAILED':
        return <XCircle className="w-6 h-6 text-red-500" />
      case 'PROCESSING':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: StageOutput['status']) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <Badge className="bg-green-500 text-white border-2 border-green-700">
            Completed
          </Badge>
        )
      case 'FAILED':
        return (
          <Badge className="bg-red-500 text-white border-2 border-red-700">
            Failed
          </Badge>
        )
      case 'PROCESSING':
        return (
          <Badge className="bg-blue-500 text-white border-2 border-blue-700">
            Processing
          </Badge>
        )
      default:
        return null
    }
  }

  const formatTime = (dateString: string | null) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleTimeString()
  }

  // Sort stages by stage number
  const sortedStages = [...stages].sort((a, b) => a.stageNumber - b.stageNumber)

  return (
    <div className="space-y-4">
      {/* Timeline */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-300" />

        {/* Stages */}
        {sortedStages.map((stage, index) => {
          const isExpanded = expandedStages.has(stage.stageNumber)
          const isLast = index === sortedStages.length - 1

          return (
            <div key={stage.id} className={`relative ${!isLast ? 'pb-8' : ''}`}>
              {/* Timeline Node */}
              <div className="absolute left-4 top-4 z-10">
                <div
                  className={`w-9 h-9 rounded-full border-4 flex items-center justify-center font-bold text-white ${
                    stage.status === 'COMPLETED'
                      ? 'bg-green-500 border-green-700'
                      : stage.status === 'FAILED'
                      ? 'bg-red-500 border-red-700'
                      : 'bg-blue-500 border-blue-700'
                  }`}
                >
                  {stage.stageNumber}
                </div>
              </div>

              {/* Stage Card */}
              <Card className="ml-20 border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
                <CardContent className="p-0">
                  {/* Stage Header */}
                  <Button
                    variant="ghost"
                    className="w-full p-6 flex items-start justify-between hover:bg-gray-50 rounded-none"
                    onClick={() => toggleStage(stage.stageNumber)}
                  >
                    <div className="flex-1 text-left space-y-2">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(stage.status)}
                        <h3 className="text-xl font-black">{stage.stageName}</h3>
                      </div>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        {getStatusBadge(stage.status)}
                        {stage.completedAt && (
                          <span>Completed at {formatTime(stage.completedAt)}</span>
                        )}
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 shrink-0" />
                    ) : (
                      <ChevronDown className="w-5 h-5 shrink-0" />
                    )}
                  </Button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="px-6 py-4 border-t-4 border-black bg-gray-50">
                      <h4 className="font-bold mb-3">Output Data:</h4>
                      <pre className="text-xs bg-white p-4 border-2 border-black rounded overflow-x-auto whitespace-pre-wrap font-mono">
                        {stage.output
                          ? JSON.stringify(JSON.parse(stage.output), null, 2)
                          : 'No output data'}
                      </pre>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )
        })}
      </div>

      {/* Empty State */}
      {sortedStages.length === 0 && (
        <div className="text-center py-20 border-4 border-black">
          <h2 className="text-2xl font-bold mb-2">No stage data</h2>
          <p className="text-gray-600">This run has not generated stage output data yet.</p>
        </div>
      )}
    </div>
  )
}

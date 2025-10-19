# 6. Components

## Frontend Component Architecture

**Next.js 14 App Router Structure**:

```
apps/web/src/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with providers
│   ├── page.tsx                  # Homepage
│   ├── prompts/
│   │   ├── page.tsx              # List prompt configurations (RSC)
│   │   ├── new/page.tsx          # Create new prompt (Client Component)
│   │   └── [id]/
│   │       ├── page.tsx          # View/edit prompt (Client Component)
│   │       └── run/page.tsx      # Execute test from this config
│   ├── run/
│   │   └── page.tsx              # Execute new test run (Client Component)
│   ├── results/
│   │   └── [runId]/
│   │       └── page.tsx          # View test results (RSC)
│   ├── comparison/
│   │   └── page.tsx              # Side-by-side brand comparison (Client Component)
│   └── api/
│       ├── pipeline/
│       │   ├── execute/route.ts
│       │   ├── status/[runId]/route.ts
│       │   └── results/[runId]/route.ts
│       ├── prompts/
│       │   ├── route.ts
│       │   └── [id]/route.ts
│       ├── cost-estimate/route.ts
│       ├── comparison/route.ts
│       └── brands/
│           └── [brandId]/
│               └── research/route.ts
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── select.tsx
│   │   ├── tabs.tsx
│   │   └── ... (30+ components)
│   ├── prompt-editor/
│   │   ├── PromptEditor.tsx      # Monaco editor wrapper
│   │   ├── ModelSelector.tsx     # Model dropdown with pricing
│   │   ├── CostEstimator.tsx     # Real-time cost calculation
│   │   └── PromptTabs.tsx        # 5-stage tab interface
│   ├── test-execution/
│   │   ├── ExecutionMonitor.tsx  # Real-time progress tracker
│   │   ├── StageProgress.tsx     # Individual stage status
│   │   └── CostTracker.tsx       # Live cost accumulation
│   └── results/
│       ├── OpportunityCard.tsx   # Single opportunity display
│       ├── OpportunityGrid.tsx   # 5-card grid layout
│       └── ComparisonView.tsx    # Side-by-side brand comparison
├── lib/
│   ├── api-client.ts             # API wrapper class
│   ├── cost-estimator.ts         # Cost calculation logic
│   ├── models.ts                 # LLM model configurations
│   ├── db.ts                     # Drizzle client
│   └── blob-client.ts            # Vercel Blob wrapper
└── stores/
    ├── prompt-editor-store.ts    # Zustand: prompt drafts
    └── execution-store.ts        # Zustand: polling state
```

## Key Components

### 1. PromptEditor Component

```typescript
// components/prompt-editor/PromptEditor.tsx
'use client';

import Editor from '@monaco-editor/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ModelSelector } from './ModelSelector';
import { CostEstimator } from './CostEstimator';

interface PromptEditorProps {
  initialConfig?: PromptConfiguration;
  onSave: (config: PromptConfiguration) => Promise<void>;
}

export function PromptEditor({ initialConfig, onSave }: PromptEditorProps) {
  const [config, setConfig] = useState(initialConfig || getDefaultConfig());
  const [activeStage, setActiveStage] = useState(1);

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Prompt Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={`stage-${activeStage}`} onValueChange={(v) => setActiveStage(Number(v.split('-')[1]))}>
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="stage-1">Stage 1</TabsTrigger>
              <TabsTrigger value="stage-2">Stage 2</TabsTrigger>
              <TabsTrigger value="stage-3">Stage 3</TabsTrigger>
              <TabsTrigger value="stage-4">Stage 4</TabsTrigger>
              <TabsTrigger value="stage-5">Stage 5</TabsTrigger>
            </TabsList>

            {[1, 2, 3, 4, 5].map((stage) => (
              <TabsContent key={stage} value={`stage-${stage}`}>
                <div className="space-y-4">
                  <Editor
                    height="400px"
                    language="markdown"
                    theme="vs-dark"
                    value={config[`stage_${stage}_prompt`]}
                    onChange={(value) =>
                      setConfig({ ...config, [`stage_${stage}_prompt`]: value || '' })
                    }
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      wordWrap: 'on',
                    }}
                  />

                  <ModelSelector
                    value={config.stage_model_overrides?.[`stage_${stage}`] || config.default_model_id}
                    onChange={(modelId) => {
                      setConfig({
                        ...config,
                        stage_model_overrides: {
                          ...config.stage_model_overrides,
                          [`stage_${stage}`]: modelId,
                        },
                      });
                    }}
                  />
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      <CostEstimator config={config} />

      <Button onClick={() => onSave(config)}>Save Configuration</Button>
    </div>
  );
}
```

### 2. ExecutionMonitor Component

```typescript
// components/test-execution/ExecutionMonitor.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { ApiClient } from '@/lib/api-client';

interface ExecutionMonitorProps {
  runId: string;
  onComplete: (results: TestRun) => void;
}

export function ExecutionMonitor({ runId, onComplete }: ExecutionMonitorProps) {
  const [status, setStatus] = useState<TestRun | null>(null);
  const client = new ApiClient();

  useEffect(() => {
    const pollStatus = async () => {
      const result = await client.getStatus(runId);
      setStatus(result);

      if (result.status === 'completed' || result.status === 'failed') {
        onComplete(result);
      }
    };

    // Poll every 2 seconds
    const interval = setInterval(pollStatus, 2000);
    pollStatus(); // Initial fetch

    return () => clearInterval(interval);
  }, [runId]);

  if (!status) return <Loader2 className="animate-spin" />;

  const stages = [
    { number: 1, name: 'Input Processing' },
    { number: 2, name: 'Signal Amplification' },
    { number: 3, name: 'General Translation' },
    { number: 4, name: 'Brand Contextualization' },
    { number: 5, name: 'Opportunity Generation' },
  ];

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-6">
          <Progress value={status.progress_percentage} />

          <div className="space-y-2">
            {stages.map((stage) => {
              const isComplete = stage.number < status.current_stage;
              const isActive = stage.number === status.current_stage;

              return (
                <div key={stage.number} className="flex items-center gap-3">
                  {isComplete ? (
                    <CheckCircle2 className="text-green-500" />
                  ) : isActive ? (
                    <Loader2 className="animate-spin text-blue-500" />
                  ) : (
                    <Circle className="text-gray-400" />
                  )}

                  <span className={isComplete || isActive ? 'font-medium' : 'text-gray-500'}>
                    Stage {stage.number}: {stage.name}
                  </span>

                  {isComplete && status.per_stage_costs?.[`stage_${stage.number}`] && (
                    <span className="ml-auto text-sm text-gray-600">
                      ${status.per_stage_costs[`stage_${stage.number}`].toFixed(3)}
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          <div className="border-t pt-4">
            <div className="flex justify-between text-sm">
              <span>Total Cost</span>
              <span className="font-mono">
                ${status.actual_cost_usd?.toFixed(3) || '0.000'} / ${status.estimated_cost_usd.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 3. API Client

```typescript
// lib/api-client.ts
export class ApiClient {
  private baseUrl = '/api';

  async executeTest(params: {
    input_id: string;
    brand_id: string;
    prompt_config_id: string;
  }): Promise<{ run_id: string }> {
    const response = await fetch(`${this.baseUrl}/pipeline/execute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async getStatus(runId: string): Promise<TestRun> {
    const response = await fetch(`${this.baseUrl}/pipeline/status/${runId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async getResults(runId: string): Promise<{
    run_id: string;
    opportunities: OpportunityCard[];
    metadata: any;
  }> {
    const response = await fetch(`${this.baseUrl}/pipeline/results/${runId}`);

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async savePromptConfig(config: Omit<PromptConfiguration, 'id' | 'created_at' | 'updated_at'>): Promise<{ id: string }> {
    const response = await fetch(`${this.baseUrl}/prompts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async estimateCost(params: {
    model_id: string;
    stage_model_overrides?: Record<string, string>;
    num_runs?: number;
  }): Promise<CostEstimation> {
    const response = await fetch(`${this.baseUrl}/cost-estimate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }
}
```

---

# 4. Data Models

## Core TypeScript Interfaces

```typescript
// Test Run (Primary Entity)
interface TestRun {
  id: string; // UUID
  status: "pending" | "running" | "completed" | "failed";
  input_id: string; // FK to InputDocument
  brand_id: string; // FK to BrandProfile
  prompt_config_id: string; // FK to PromptConfiguration

  // Model selection
  models_used: {
    stage_1: string; // Model ID used for Stage 1
    stage_2: string;
    stage_3: string;
    stage_4: string;
    stage_5: string;
  };

  // Cost tracking
  estimated_cost_usd: number | null;
  actual_cost_usd: number | null;
  per_stage_costs: {
    stage_1: number;
    stage_2: number;
    stage_3: number;
    stage_4: number;
    stage_5: number;
  } | null;

  // Progress tracking
  current_stage: number; // 1-5
  stage_outputs: {
    stage_1_path: string | null; // Blob storage path
    stage_2_path: string | null;
    stage_3_path: string | null;
    stage_4_path: string | null;
    stage_5_path: string | null; // Final opportunity cards
  };

  // Metadata
  created_at: Date;
  updated_at: Date;
  completed_at: Date | null;
  error_message: string | null;
}

// Prompt Configuration (Reusable Template)
interface PromptConfiguration {
  id: string; // UUID
  name: string; // User-defined name
  description: string | null;

  // Stage prompts
  stage_1_prompt: string;
  stage_2_prompt: string;
  stage_3_prompt: string;
  stage_4_prompt: string;
  stage_5_prompt: string;

  // Model selection
  default_model_id: string; // Default model for all stages
  stage_model_overrides: {
    stage_1?: string; // Optional per-stage overrides
    stage_2?: string;
    stage_3?: string;
    stage_4?: string;
    stage_5?: string;
  };

  // Metadata
  created_at: Date;
  updated_at: Date;
  is_default: boolean; // Mark as default configuration
}

// Brand Profile (Metadata Only)
interface BrandProfile {
  id: string; // e.g., "lactalis-canada"
  display_name: string; // "Lactalis Canada"
  industry: string;
  research_file_path: string; // Blob storage path to research markdown
  last_updated: Date;
}

// Input Document (Innovation Trend/Signal)
interface InputDocument {
  id: string; // e.g., "sustainable-packaging-trends"
  title: string;
  description: string;
  source: string; // URL or document source
  content_path: string; // Blob storage path
  created_at: Date;
}

// Stage Output (Intermediate Results)
interface StageOutput {
  run_id: string; // FK to TestRun
  stage: number; // 1-5
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  duration_ms: number;
  model_id: string;
  output_path: string; // Blob storage path
  created_at: Date;
}

// Opportunity Card (Final Output)
interface OpportunityCard {
  run_id: string; // FK to TestRun
  opportunity_number: number; // 1-5
  title: string;
  strategic_rationale: string;
  implementation_approach: string;
  success_metrics: string;
  risks_and_mitigations: string;
  estimated_timeline: string;
  estimated_investment: string;
  markdown_path: string; // Blob storage path
  created_at: Date;
}

// Research Data (Loaded from Blob)
interface ResearchData {
  brand_id: string;
  sections: {
    brand_overview: ResearchSection;
    product_portfolio: ResearchSection;
    recent_innovations: ResearchSection; // CRITICAL for Stage 4
    strategic_priorities: ResearchSection;
    target_customers: ResearchSection;
    sustainability: ResearchSection;
    competitive_context: ResearchSection;
    recent_news: ResearchSection;
  };
  key_insights: {
    innovation_dna: string;
    strategic_north_star: string;
    opportunity_whitespace: string;
  };
  total_data_points: number; // Target: 120+
  research_date: Date;
}

interface ResearchSection {
  title: string;
  content: string; // Markdown content
  data_points: number;
}
```

## Cost Estimation Model

```typescript
interface CostEstimation {
  total_cost_usd: number;
  per_stage_costs: {
    stage_1: number;
    stage_2: number;
    stage_3: number;
    stage_4: number;
    stage_5: number;
  };
  breakdown: Array<{
    stage: number;
    model_id: string;
    estimated_input_tokens: number;
    estimated_output_tokens: number;
    cost_usd: number;
  }>;
}
```

---

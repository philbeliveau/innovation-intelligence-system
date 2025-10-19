# 7. Database Schema

## PostgreSQL Tables (Drizzle ORM)

```typescript
// db/schema.ts
import { pgTable, uuid, varchar, text, jsonb, timestamp, integer, numeric, boolean } from 'drizzle-orm/pg-core';

export const testRuns = pgTable('test_runs', {
  id: uuid('id').primaryKey().defaultRandom(),
  status: varchar('status', { length: 20 }).notNull(), // pending, running, completed, failed

  // Foreign keys
  inputId: varchar('input_id', { length: 100 }).notNull(),
  brandId: varchar('brand_id', { length: 100 }).notNull(),
  promptConfigId: uuid('prompt_config_id').notNull(),

  // Model selection
  modelsUsed: jsonb('models_used').notNull(), // { stage_1: string, ..., stage_5: string }

  // Cost tracking
  estimatedCostUsd: numeric('estimated_cost_usd', { precision: 10, scale: 4 }),
  actualCostUsd: numeric('actual_cost_usd', { precision: 10, scale: 4 }),
  perStageCosts: jsonb('per_stage_costs'), // { stage_1: number, ..., stage_5: number }

  // Progress
  currentStage: integer('current_stage').default(0),
  stageOutputs: jsonb('stage_outputs').default('{}'), // { stage_1_path: string, ... }

  // Metadata
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  errorMessage: text('error_message'),
});

export const promptConfigurations = pgTable('prompt_configurations', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: varchar('name', { length: 255 }).notNull(),
  description: text('description'),

  // Stage prompts
  stage1Prompt: text('stage_1_prompt').notNull(),
  stage2Prompt: text('stage_2_prompt').notNull(),
  stage3Prompt: text('stage_3_prompt').notNull(),
  stage4Prompt: text('stage_4_prompt').notNull(),
  stage5Prompt: text('stage_5_prompt').notNull(),

  // Model selection
  defaultModelId: varchar('default_model_id', { length: 100 }).notNull(),
  stageModelOverrides: jsonb('stage_model_overrides').default('{}'),

  // Metadata
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  isDefault: boolean('is_default').default(false),
});

export const brandProfiles = pgTable('brand_profiles', {
  id: varchar('id', { length: 100 }).primaryKey(), // e.g., "lactalis-canada"
  displayName: varchar('display_name', { length: 255 }).notNull(),
  industry: varchar('industry', { length: 100 }),
  researchFilePath: text('research_file_path').notNull(), // Blob storage path
  lastUpdated: timestamp('last_updated').defaultNow(),
});

export const inputDocuments = pgTable('input_documents', {
  id: varchar('id', { length: 100 }).primaryKey(),
  title: varchar('title', { length: 255 }).notNull(),
  description: text('description'),
  source: text('source'),
  contentPath: text('content_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const stageOutputs = pgTable('stage_outputs', {
  id: uuid('id').primaryKey().defaultRandom(),
  runId: uuid('run_id').notNull().references(() => testRuns.id),
  stage: integer('stage').notNull(), // 1-5

  // Execution metrics
  inputTokens: integer('input_tokens').notNull(),
  outputTokens: integer('output_tokens').notNull(),
  costUsd: numeric('cost_usd', { precision: 10, scale: 4 }).notNull(),
  durationMs: integer('duration_ms').notNull(),
  modelId: varchar('model_id', { length: 100 }).notNull(),

  // Output
  outputPath: text('output_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const opportunityCards = pgTable('opportunity_cards', {
  id: uuid('id').primaryKey().defaultRandom(),
  runId: uuid('run_id').notNull().references(() => testRuns.id),
  opportunityNumber: integer('opportunity_number').notNull(), // 1-5

  // Content
  title: varchar('title', { length: 255 }).notNull(),
  strategicRationale: text('strategic_rationale').notNull(),
  implementationApproach: text('implementation_approach').notNull(),
  successMetrics: text('success_metrics').notNull(),
  risksAndMitigations: text('risks_and_mitigations').notNull(),
  estimatedTimeline: varchar('estimated_timeline', { length: 100 }),
  estimatedInvestment: varchar('estimated_investment', { length: 100 }),

  // Storage
  markdownPath: text('markdown_path').notNull(), // Blob storage path
  createdAt: timestamp('created_at').defaultNow().notNull(),
});
```

## Indexes

```sql
-- Performance indexes
CREATE INDEX idx_test_runs_status ON test_runs(status);
CREATE INDEX idx_test_runs_created_at ON test_runs(created_at DESC);
CREATE INDEX idx_test_runs_brand ON test_runs(brand_id);
CREATE INDEX idx_test_runs_input ON test_runs(input_id);
CREATE INDEX idx_stage_outputs_run ON stage_outputs(run_id);
CREATE INDEX idx_opportunity_cards_run ON opportunity_cards(run_id);
CREATE INDEX idx_prompt_configs_default ON prompt_configurations(is_default) WHERE is_default = true;
```

---

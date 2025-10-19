# 5. API Specification

## REST API Endpoints

**Base URL**: `https://pipeline.yourdomain.com/api`

### 1. Execute Pipeline Test

```http
POST /api/pipeline/execute
Content-Type: application/json
Authorization: Bearer {token}

{
  "input_id": "sustainable-packaging-trends",
  "brand_id": "lactalis-canada",
  "prompt_config_id": "config-123"
}
```

**Response** (202 Accepted):
```json
{
  "run_id": "run-abc-123",
  "status": "pending",
  "estimated_cost_usd": 0.42,
  "models_used": {
    "stage_1": "deepseek/deepseek-chat",
    "stage_2": "deepseek/deepseek-chat",
    "stage_3": "deepseek/deepseek-chat",
    "stage_4": "anthropic/claude-sonnet-4-20250514",
    "stage_5": "deepseek/deepseek-chat"
  }
}
```

### 2. Get Pipeline Status (Polling)

```http
GET /api/pipeline/status/{runId}
```

**Response** (200 OK):
```json
{
  "run_id": "run-abc-123",
  "status": "running",
  "current_stage": 3,
  "progress_percentage": 60,
  "models_used": { /* ... */ },
  "estimated_cost_usd": 0.42,
  "actual_cost_usd": 0.18,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": null,
    "stage_5": null
  },
  "error_message": null,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:35:00Z"
}
```

**Response when completed**:
```json
{
  "run_id": "run-abc-123",
  "status": "completed",
  "current_stage": 5,
  "progress_percentage": 100,
  "actual_cost_usd": 0.38,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": 0.15,
    "stage_5": 0.05
  },
  "opportunities": [
    {
      "number": 1,
      "title": "Plant-Based Dairy Line Extension",
      "markdown_url": "https://blob.vercel-storage.com/runs/run-abc-123/opportunity_1.md"
    },
    // ... 4 more opportunities
  ],
  "completed_at": "2025-01-15T10:40:00Z"
}
```

### 3. Get Run Results

```http
GET /api/pipeline/results/{runId}
```

**Response** (200 OK):
```json
{
  "run_id": "run-abc-123",
  "input": {
    "id": "sustainable-packaging-trends",
    "title": "Sustainable Packaging Innovations 2025"
  },
  "brand": {
    "id": "lactalis-canada",
    "display_name": "Lactalis Canada"
  },
  "opportunities": [
    {
      "number": 1,
      "title": "Plant-Based Dairy Line Extension",
      "strategic_rationale": "...",
      "implementation_approach": "...",
      "success_metrics": "...",
      "risks_and_mitigations": "...",
      "estimated_timeline": "12-18 months",
      "estimated_investment": "$2-5M",
      "markdown_content": "# Opportunity #1\n\n..."
    }
    // ... 4 more
  ],
  "metadata": {
    "actual_cost_usd": 0.38,
    "models_used": { /* ... */ },
    "completed_at": "2025-01-15T10:40:00Z"
  }
}
```

### 4. Save Prompt Configuration

```http
POST /api/prompts
Content-Type: application/json

{
  "name": "V2 - Enhanced Brand Context",
  "description": "Uses longer prompts for Stage 4 with explicit research dimensions",
  "stage_1_prompt": "Extract key insights from this innovation trend...",
  "stage_2_prompt": "Amplify weak signals by...",
  "stage_3_prompt": "Translate into general strategic concepts...",
  "stage_4_prompt": "Contextualize for {brand_name} using:\n\n## Recent Innovations\n{recent_innovations}\n\n...",
  "stage_5_prompt": "Generate exactly 5 opportunity cards...",
  "default_model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": {
    "stage_4": "anthropic/claude-sonnet-4-20250514"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "config-456",
  "name": "V2 - Enhanced Brand Context",
  "created_at": "2025-01-15T11:00:00Z"
}
```

### 5. Get Prompt Configuration

```http
GET /api/prompts/{configId}
```

**Response** (200 OK):
```json
{
  "id": "config-456",
  "name": "V2 - Enhanced Brand Context",
  "description": "...",
  "stage_1_prompt": "...",
  // ... all prompts
  "default_model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": { /* ... */ },
  "created_at": "2025-01-15T11:00:00Z",
  "updated_at": "2025-01-15T11:00:00Z"
}
```

### 6. Cost Estimation

```http
POST /api/cost-estimate
Content-Type: application/json

{
  "model_id": "deepseek/deepseek-chat",
  "stage_model_overrides": {
    "stage_4": "anthropic/claude-sonnet-4-20250514"
  },
  "num_runs": 10
}
```

**Response** (200 OK):
```json
{
  "total_cost_usd": 4.20,
  "cost_per_run": 0.42,
  "per_stage_costs": {
    "stage_1": 0.05,
    "stage_2": 0.06,
    "stage_3": 0.07,
    "stage_4": 0.19,
    "stage_5": 0.05
  },
  "breakdown": [
    {
      "stage": 1,
      "model_id": "deepseek/deepseek-chat",
      "estimated_input_tokens": 5000,
      "estimated_output_tokens": 2000,
      "cost_usd": 0.05
    }
    // ... stages 2-5
  ]
}
```

### 7. Compare Opportunities Across Brands

```http
POST /api/comparison
Content-Type: application/json

{
  "input_id": "sustainable-packaging-trends",
  "brand_ids": ["lactalis-canada", "mccormick-usa"],
  "prompt_config_id": "config-456"
}
```

**Response** (200 OK):
```json
{
  "input": {
    "id": "sustainable-packaging-trends",
    "title": "Sustainable Packaging Innovations 2025"
  },
  "comparisons": [
    {
      "brand_id": "lactalis-canada",
      "brand_name": "Lactalis Canada",
      "run_id": "run-xyz-789",
      "status": "completed",
      "opportunities": [ /* 5 opportunities */ ],
      "actual_cost_usd": 0.38
    },
    {
      "brand_id": "mccormick-usa",
      "brand_name": "McCormick USA",
      "run_id": "run-xyz-790",
      "status": "completed",
      "opportunities": [ /* 5 opportunities */ ],
      "actual_cost_usd": 0.41
    }
  ]
}
```

### 8. Get Brand Research Data

```http
GET /api/brands/{brandId}/research
```

**Response** (200 OK):
```json
{
  "brand_id": "lactalis-canada",
  "display_name": "Lactalis Canada",
  "sections": {
    "brand_overview": {
      "title": "Brand Overview & Positioning",
      "content": "...",
      "data_points": 18
    },
    "recent_innovations": {
      "title": "Recent Innovations (Last 18 Months)",
      "content": "...",
      "data_points": 22
    }
    // ... 6 more sections
  },
  "key_insights": {
    "innovation_dna": "Lactalis focuses on product innovation...",
    "strategic_north_star": "Growth through premium positioning...",
    "opportunity_whitespace": "Limited presence in plant-based alternatives..."
  },
  "total_data_points": 127,
  "research_date": "2025-01-15T00:00:00Z"
}
```

---

*(Continued in next section...)*

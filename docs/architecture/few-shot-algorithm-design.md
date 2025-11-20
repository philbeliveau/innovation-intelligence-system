# Few-Shot Learning Algorithm Design

## Overview

This guide defines the algorithm and data structures for the few-shot learning system that improves pipeline output quality over time. Extracted from Story 11.3 to separate requirements from technical specifications.

**Target Story:** 11.3 - Few-Shot Learning System
**Purpose:** Enable pipeline to learn from manually curated "Good" examples

---

## System Architecture

```
┌──────────────────────────────────────────────┐
│          Gradio UI Quality Tagging           │
│  User marks experiment as "Good"             │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│      FewShotManager.save_example()           │
│  - Generate unique ID                        │
│  - Save to stage-specific folder             │
│  - Update metadata.json                      │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│   /backend/experimentation/                  │
│   successful_examples/                       │
│     ├── stage_0/                             │
│     │   ├── example_20251119_a3f8b2.json     │
│     │   ├── example_20251119_c7d1e9.json     │
│     │   └── metadata.json                    │
│     ├── stage_1/                             │
│     └── ...stage_6/                          │
└──────────────────────────────────────────────┘

                 ▲
                 │
                 │ (Selection)
                 │
┌──────────────────────────────────────────────┐
│    ExampleSelector.select_relevant()         │
│  - Load examples for stage                   │
│  - Calculate relevance scores                │
│  - Return top N examples                     │
└────────────────┬─────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│      Pipeline Stage Execution                │
│  - Load prompt template                      │
│  - Inject selected examples                  │
│  - Execute LLM call                          │
│  - Track which examples used                 │
└──────────────────────────────────────────────┘
```

---

## Example JSON Schema

### Individual Example File
**Location:** `/backend/experimentation/successful_examples/{stage_n}/example_{timestamp}_{hash}.json`

```json
{
  "id": "example_20251119_a3f8b2",
  "created_at": "2025-11-19T14:32:18Z",
  "stage": 1,
  "quality_score": "good",
  "usage_count": 0,
  "last_used_at": null,

  "brand_context": {
    "brand_name": "Lactalis Canada",
    "industry": "Dairy & Food Products",
    "country": "Canada",
    "product_portfolio": ["Milk", "Cheese", "Yogurt"]
  },

  "input": {
    "pdf_text": "truncated for storage...",
    "trend_report_name": "WGSN-FC27-Emotions.pdf",
    "previous_stage_output": { }
  },

  "prompt_used": "You are analyzing trend reports to extract...",

  "output": {
    "trends": [
      {
        "trend_id": "witherwill_001",
        "name": "Witherwill",
        "lifecycle_stage": "ACCELERATING",
        "abstraction_ladder": {
          "L1_domain_specific": "Consumers overwhelmed by dairy choices",
          "L2_category": "Shoppers want simplified food selection",
          "L3_cross_category": "People seek reduced cognitive load in decisions",
          "L4_universal": "Humans desire freedom from trivial choices"
        }
      }
    ]
  },

  "metadata": {
    "pipeline_version": "1.0",
    "execution_time_seconds": 12,
    "token_usage": {
      "input": 8234,
      "output": 1567
    },
    "model_used": "anthropic/claude-3-opus-20240229"
  }
}
```

### Metadata File Per Stage
**Location:** `/backend/experimentation/successful_examples/{stage_n}/metadata.json`

```json
{
  "stage": 1,
  "total_examples": 15,
  "last_updated": "2025-11-19T14:32:18Z",
  "usage_stats": {
    "total_uses": 127,
    "examples_by_quality": {
      "good": 15,
      "needs_work": 0,
      "failed": 0
    }
  },
  "top_performers": [
    {
      "example_id": "example_20251119_a3f8b2",
      "usage_count": 23,
      "success_correlation": 0.87
    }
  ]
}
```

---

## Relevance Scoring Algorithm

### Weighted Scoring Formula

```python
def calculate_relevance_score(example, current_context):
    """
    Calculate relevance score for example selection

    Score = (0.6 × brand_similarity) + (0.3 × recency) + (0.1 × quality)
    """

    # 1. Brand Similarity (60% weight)
    brand_score = 0.0

    # Industry exact match: +0.4
    if example["brand_context"]["industry"] == current_context["industry"]:
        brand_score += 0.4
    # Industry category match (e.g., "Food" in both): +0.2
    elif has_category_overlap(example["brand_context"]["industry"], current_context["industry"]):
        brand_score += 0.2

    # Geography exact match: +0.2
    if example["brand_context"]["country"] == current_context["country"]:
        brand_score += 0.2
    # Same continent: +0.1
    elif same_continent(example["brand_context"]["country"], current_context["country"]):
        brand_score += 0.1

    # Portfolio overlap (Jaccard similarity): 0.0-0.4
    portfolio_score = calculate_portfolio_similarity(
        example["brand_context"]["product_portfolio"],
        current_context["product_portfolio"]
    )
    brand_score += (portfolio_score * 0.4)

    # Normalize to 0.0-1.0
    brand_similarity = min(brand_score, 1.0)

    # 2. Recency Score (30% weight)
    days_old = (datetime.now() - parse_date(example["created_at"])).days
    recency = max(0, 1 - (days_old / 90))  # Decay over 90 days

    # 3. Quality Score (10% weight)
    quality_map = {"good": 1.0, "needs_work": 0.5, "failed": 0.0}
    quality = quality_map.get(example["quality_score"], 0.5)

    # Weighted combination
    total_score = (0.6 * brand_similarity) + (0.3 * recency) + (0.1 * quality)

    return total_score, {
        "brand_similarity": brand_similarity,
        "recency": recency,
        "quality": quality,
        "total": total_score
    }
```

### Helper Functions

```python
def calculate_portfolio_similarity(portfolio_a, portfolio_b):
    """Jaccard similarity for product portfolios"""
    set_a = set([normalize_product(p) for p in portfolio_a])
    set_b = set([normalize_product(p) for p in portfolio_b])

    intersection = len(set_a & set_b)
    union = len(set_a | set_b)

    return intersection / union if union > 0 else 0.0

def normalize_product(product_name):
    """Normalize product names for comparison"""
    # "Milk (2%, whole)" → "milk"
    return product_name.lower().split('(')[0].strip()

def same_continent(country_a, country_b):
    """Check if countries on same continent"""
    continent_map = {
        "USA": "North America",
        "Canada": "North America",
        "France": "Europe",
        "Germany": "Europe",
        # ... expand as needed
    }
    return continent_map.get(country_a) == continent_map.get(country_b)
```

---

## Example Selection Algorithm

```python
class ExampleSelector:
    def __init__(self, storage_path="/backend/experimentation/successful_examples/"):
        self.storage_path = storage_path
        self.cache = {}  # LRU cache for frequently used examples

    def select_relevant(self, stage: int, current_context: dict, max_examples: int = 2):
        """
        Select most relevant examples for current pipeline run

        Args:
            stage: Pipeline stage (0-6)
            current_context: Current brand context and inputs
            max_examples: Maximum examples to return (default: 2)

        Returns:
            List of example objects sorted by relevance
        """

        # 1. Load all examples for stage
        stage_path = Path(self.storage_path) / f"stage_{stage}"
        examples = self._load_stage_examples(stage_path)

        if not examples:
            return []

        # 2. Calculate relevance scores
        scored_examples = []
        for example in examples:
            score, breakdown = calculate_relevance_score(example, current_context)
            scored_examples.append({
                "example": example,
                "score": score,
                "breakdown": breakdown
            })

        # 3. Sort by score (descending)
        scored_examples.sort(key=lambda x: x["score"], reverse=True)

        # 4. Filter by threshold and limit
        threshold = 0.7  # Minimum relevance score
        relevant = [
            se["example"]
            for se in scored_examples
            if se["score"] >= threshold
        ][:max_examples]

        # 5. Update usage tracking
        for example in relevant:
            self._increment_usage_count(example["id"], stage)

        return relevant

    def _load_stage_examples(self, stage_path):
        """Load all examples from stage directory"""
        examples = []

        if not stage_path.exists():
            return examples

        for example_file in stage_path.glob("example_*.json"):
            with open(example_file, 'r') as f:
                examples.append(json.load(f))

        return examples

    def _increment_usage_count(self, example_id, stage):
        """Track example usage in metadata"""
        metadata_path = Path(self.storage_path) / f"stage_{stage}" / "metadata.json"

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        metadata["usage_stats"]["total_uses"] += 1

        # Update specific example usage count
        # (Implementation details omitted for brevity)

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
```

---

## Prompt Injection Strategy

### Token Budget Management

```python
class PromptInjector:
    def __init__(self, max_total_tokens=100_000):
        self.max_total_tokens = max_total_tokens

    def inject_examples(self, base_prompt: str, examples: list, current_input: dict):
        """
        Inject examples into prompt while respecting token limits

        Token allocation:
        - Base prompt: ~2,000 tokens
        - Current input: ~10,000 tokens
        - Examples: Remaining budget (~88,000 tokens)
        - Reserve for output: ~30,000 tokens

        Max examples tokens: ~58,000
        """

        # 1. Estimate token counts
        base_tokens = estimate_tokens(base_prompt)
        input_tokens = estimate_tokens(json.dumps(current_input))

        available_for_examples = self.max_total_tokens - base_tokens - input_tokens - 30_000

        # 2. Format examples
        formatted_examples = []
        used_tokens = 0

        for i, example in enumerate(examples, 1):
            formatted = self._format_example(example, i)
            example_tokens = estimate_tokens(formatted)

            if used_tokens + example_tokens > available_for_examples:
                break  # Stop adding examples if budget exceeded

            formatted_examples.append(formatted)
            used_tokens += example_tokens

        # 3. Inject into prompt
        examples_section = "\n\n".join(formatted_examples)

        final_prompt = f"""
{base_prompt}

## Few-Shot Examples

The following examples demonstrate high-quality outputs for this stage:

{examples_section}

## Your Task

Now process the following input using the same approach demonstrated above:

{json.dumps(current_input, indent=2)}
"""

        return final_prompt, {
            "base_tokens": base_tokens,
            "input_tokens": input_tokens,
            "example_tokens": used_tokens,
            "examples_included": len(formatted_examples)
        }

    def _format_example(self, example, index):
        """Format example for LLM consumption"""
        return f"""
### Example {index}

**Brand Context:**
- Industry: {example['brand_context']['industry']}
- Geography: {example['brand_context']['country']}
- Products: {', '.join(example['brand_context']['product_portfolio'][:3])}

**Input:**
```json
{json.dumps(example['input'], indent=2)[:500]}... (truncated)
```

**Output:**
```json
{json.dumps(example['output'], indent=2)[:1000]}... (truncated)
```

**Quality Notes:** This example was manually tagged as "Good" by innovation researchers.
"""

def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars ≈ 1 token)"""
    return len(text) // 4
```

---

## Performance Optimization

### LRU Cache for Frequently Used Examples

```python
from functools import lru_cache
from collections import OrderedDict

class ExampleCache:
    def __init__(self, max_size=50):
        self.cache = OrderedDict()
        self.max_size = max_size

    def get(self, example_id):
        """Get example from cache (moves to end)"""
        if example_id in self.cache:
            self.cache.move_to_end(example_id)
            return self.cache[example_id]
        return None

    def put(self, example_id, example_data):
        """Add example to cache (evict oldest if full)"""
        if example_id in self.cache:
            self.cache.move_to_end(example_id)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)  # Remove oldest
            self.cache[example_id] = example_data
```

### Lazy Loading Strategy

```python
class LazyExampleLoader:
    def __init__(self, stage_path):
        self.stage_path = stage_path
        self._metadata = None
        self._examples = {}

    def load_metadata(self):
        """Load only metadata.json (lightweight)"""
        if self._metadata is None:
            metadata_path = self.stage_path / "metadata.json"
            with open(metadata_path, 'r') as f:
                self._metadata = json.load(f)
        return self._metadata

    def load_example(self, example_id):
        """Load full example only when needed"""
        if example_id not in self._examples:
            example_path = self.stage_path / f"{example_id}.json"
            with open(example_path, 'r') as f:
                self._examples[example_id] = json.load(f)
        return self._examples[example_id]
```

---

## Configuration

```python
# /backend/experimentation/config.py

class FewShotConfig:
    """Few-shot learning configuration"""

    # Feature toggle
    ENABLED = os.getenv("FEW_SHOT_ENABLED", "true").lower() == "true"

    # Example limits
    MAX_EXAMPLES_PER_STAGE = int(os.getenv("MAX_EXAMPLES_PER_STAGE", "2"))

    # Relevance scoring
    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.7"))
    BRAND_SIMILARITY_WEIGHT = 0.6
    RECENCY_WEIGHT = 0.3
    QUALITY_WEIGHT = 0.1

    # Performance
    CACHE_SIZE = int(os.getenv("EXAMPLE_CACHE_SIZE", "50"))
    RECENCY_DECAY_DAYS = 90  # Examples lose relevance after 90 days

    # Storage
    STORAGE_PATH = "/backend/experimentation/successful_examples/"

    # Token management
    MAX_EXAMPLE_TOKENS = 58_000  # Per pipeline run
```

---

## Usage Tracking Schema

### Database Extension (Prisma)

```prisma
model ExampleUsage {
  id              String   @id @default(uuid())
  example_id      String
  run_id          String
  stage           Int
  used_at         DateTime @default(now())
  output_quality  String   // "good" | "needs_work" | "failed"

  @@index([example_id])
  @@index([run_id])
}
```

### Tracking Implementation

```python
class UsageTracker:
    def __init__(self, prisma_client):
        self.db = prisma_client

    async def track_usage(self, example_id, run_id, stage, output_quality):
        """Log example usage to database"""
        await self.db.example_usage.create({
            "example_id": example_id,
            "run_id": run_id,
            "stage": stage,
            "output_quality": output_quality
        })

    async def get_example_performance(self, example_id):
        """Calculate success correlation for example"""
        usages = await self.db.example_usage.find_many({
            "where": {"example_id": example_id}
        })

        total_uses = len(usages)
        successful_uses = len([u for u in usages if u["output_quality"] == "good"])

        return {
            "example_id": example_id,
            "total_uses": total_uses,
            "successful_uses": successful_uses,
            "success_rate": successful_uses / total_uses if total_uses > 0 else 0
        }
```

---

## Backup & Version Control

### Git Integration

```bash
# Ensure examples directory tracked in git
git add backend/experimentation/successful_examples/

# Commit examples regularly
git commit -m "Update few-shot examples: +3 Stage 1 examples"
```

### Database Backup

```python
class ExampleBackup:
    def export_to_db(self, prisma_client):
        """Backup examples to database JSONB column"""
        all_examples = self._collect_all_examples()

        prisma_client.system_config.upsert({
            "where": {"key": "few_shot_examples_backup"},
            "update": {
                "value": json.dumps(all_examples),
                "updated_at": datetime.now()
            },
            "create": {
                "key": "few_shot_examples_backup",
                "value": json.dumps(all_examples)
            }
        })

    def restore_from_db(self, prisma_client):
        """Restore examples from database backup"""
        backup = prisma_client.system_config.find_unique({
            "where": {"key": "few_shot_examples_backup"}
        })

        if backup:
            examples = json.loads(backup["value"])
            self._write_examples_to_filesystem(examples)
```

---

## Testing Strategy

### Unit Tests

```python
def test_relevance_scoring():
    """Test relevance score calculation"""
    example = {
        "brand_context": {
            "industry": "Dairy & Food Products",
            "country": "Canada",
            "product_portfolio": ["Milk", "Cheese"]
        },
        "created_at": "2025-11-10T00:00:00Z",
        "quality_score": "good"
    }

    current_context = {
        "industry": "Dairy & Food Products",
        "country": "Canada",
        "product_portfolio": ["Milk", "Yogurt"]
    }

    score, breakdown = calculate_relevance_score(example, current_context)

    assert breakdown["brand_similarity"] > 0.8  # High industry+geography match
    assert breakdown["recency"] > 0.7  # Recent (9 days old)
    assert breakdown["quality"] == 1.0  # Good quality
    assert score > 0.75  # High overall relevance
```

---

## References

- **Story 11.3:** `/docs/stories/11.3.few-shot-learning.md`
- **PRD Section:** "Few-Shot Learning" (lines 130-142)
- **Example Manager:** `/backend/experimentation/few_shot_manager.py`

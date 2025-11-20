# Innovation Pipeline Experimentation Lab

## 🚀 Overview

This experimentation framework allows you to test and optimize the innovation pipeline with advanced features:

1. **Few-Shot Example Learning** - Pipeline learns from successful outputs
2. **Automatic Quality Scoring** - Identifies high-quality results without manual review
3. **Prompt Template Library** - Save and reuse successful prompts
4. **Trend Filtering & Prioritization** - Focus on most relevant trends

## 📁 File Structure

```
backend/experimentation/
├── gradio_prompt_lab.py          # Basic prompt editing interface
├── enhanced_gradio_lab.py        # FULL interface with all features
├── few_shot_manager.py           # Few-shot example system
├── quality_scorer.py             # Automatic quality scoring
├── prompt_template_library.py    # Template management
├── trend_filter.py               # Trend filtering/prioritization
└── README.md                      # This file
```

## 🎯 Quick Start

### 1. Basic Setup
```bash
# Install dependencies
pip install gradio PyPDF2 httpx

# Set API key
export OPENROUTER_API_KEY=your_key_here

# Run basic interface
python gradio_prompt_lab.py
```

### 2. Enhanced Interface (Recommended)
```bash
# Run the full-featured interface
python enhanced_gradio_lab.py

# Opens at http://localhost:7860
# Also creates shareable link for founder
```

## 🔧 Features in Detail

### 1. Few-Shot Example Injection (`few_shot_manager.py`)

**What it does:** Automatically adds successful examples to prompts, improving LLM performance.

**How it works:**
- Stores high-quality outputs (score > 0.8) as examples
- Injects 2-3 best examples into prompts
- Different formatting styles (detailed, simple, JSON)

**Usage in pipeline:**
```python
from few_shot_manager import FewShotExampleManager

manager = FewShotExampleManager()

# Enhance prompt with examples
enhanced_prompt = manager.inject_into_prompt(
    original_prompt,
    stage="stage_2",
    n_examples=2
)

# Auto-save if quality is high
manager.auto_save_if_good(
    stage="stage_2",
    input_context={"trends": trends},
    output=insights,
    quality_scores={"relevance": 0.9}
)
```

### 2. Automatic Quality Scoring (`quality_scorer.py`)

**What it does:** Scores pipeline outputs without manual review.

**Scoring criteria by stage:**

**Stage 1 (Trends):**
- Completeness of L1-L4 abstractions
- Emotional driver richness
- Lifecycle stage presence

**Stage 2 (Insights):**
- Multi-trend convergence
- Brand specificity
- Consumer needs (functional/emotional/social)

**Stage 3 (Techniques):**
- Technique selection clarity
- Application specificity
- CPG example quality

**Stage 4 (Concepts):**
- Concept name memorability
- Description completeness
- Feasibility assessment

**Usage:**
```python
from quality_scorer import QualityScorer

scorer = QualityScorer()
results = scorer.score_full_pipeline(
    stage_outputs,
    brand_context,
    creativity_level=0.7
)

print(scorer.format_report(results))
```

### 3. Prompt Template Library (`prompt_template_library.py`)

**What it does:** Manages a library of proven prompt templates.

**Template categories:**
- **baseline** - Standard prompts
- **emotional** - Emotion-focused
- **strategic** - Lifecycle-based
- **detailed** - Evidence-heavy

**Usage:**
```python
from prompt_template_library import PromptTemplateLibrary

library = PromptTemplateLibrary()

# Get best performing template
best = library.get_best_template("stage_2")

# Get specific category
emotional = library.get_template(
    stage="stage_2",
    name="emotional_convergence"
)

# Record performance
library.record_usage(
    template_id,
    quality_score=0.85
)
```

### 4. Trend Filtering (`trend_filter.py`)

**What it does:** Filters and prioritizes trends before processing.

**Filter presets:**
- **early_innovation** - Focus on EMERGING trends
- **validated_trends** - ACCELERATING trends only
- **broad_exploration** - All lifecycle stages
- **emotional_focus** - Specific emotional territories

**Scoring factors:**
1. Lifecycle stage fit (25%)
2. Emotional relevance (20%)
3. Brand keywords (15%)
4. Abstraction quality (25%)
5. Industry fit (15%)

**Usage:**
```python
from trend_filter import TrendFilter, FILTER_PRESETS

filter_system = TrendFilter(FILTER_PRESETS["early_innovation"])

processed, skipped = filter_system.filter_trends(
    all_trends,
    brand_context,
    strategy="balanced"
)

print(f"Processing {len(processed)} of {len(all_trends)} trends")
```

## 📊 Enhanced Interface Features

The `enhanced_gradio_lab.py` combines all features:

### Feature Toggles
- ✅ **Use Few-Shot Examples** - Add 1-5 examples to prompts
- ✅ **Use Template Library** - Select proven templates
- ✅ **Enable Trend Filtering** - Process only relevant trends
- ✅ **Enable Quality Scoring** - Get automatic quality metrics

### Configuration Options
- **Template Strategy**: best, random, or category-specific
- **Filter Preset**: early_innovation, validated_trends, etc.
- **Few-Shot Count**: Number of examples (1-5)
- **Max Trends**: Limit processing (1-7)

### Outputs
1. **Processed Trends** - After filtering
2. **Generated Insights** - With convergence patterns
3. **Filter Report** - Why trends were kept/skipped
4. **Quality Report** - Detailed scoring by stage
5. **Summary** - Overall pipeline results

## 🔄 Workflow

### Experimentation Flow

1. **Upload** WGSN/Mintel trend report PDF
2. **Configure** enhancement features
3. **Run** pipeline with real LLM calls
4. **Review** quality scores
5. **Save** successful outputs as examples
6. **Iterate** with different configurations

### Learning Loop

```
Run Pipeline → Score Quality → Save Good Examples → Enhance Future Prompts
      ↑                                                           ↓
      ←←←←←←←←←←← Better Results ←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

## 🎯 Optimization Tips

### Finding Best Configuration

1. **Start broad**: Use "broad_exploration" filter preset
2. **Test templates**: Try different template categories
3. **Add examples**: Enable few-shot after 5+ runs
4. **Refine filtering**: Narrow to high-relevance trends
5. **Track scores**: Focus on configurations scoring > 0.8

### Performance Metrics to Track

- **Stage 1**: Trend extraction completeness
- **Stage 2**: Insight convergence quality
- **Stage 3**: Technique application clarity
- **Stage 4**: Concept feasibility
- **Overall**: Pipeline average score

## 📈 Statistics & Monitoring

Access statistics in the interface:

```python
# Few-shot library stats
{
  "stage_1": {"count": 12, "avg_score": 0.85},
  "stage_2": {"count": 18, "avg_score": 0.88},
  "overall": {"total_examples": 42, "avg_quality": 0.83}
}

# Template performance
- emotional_convergence: 0.92 avg score (15 uses)
- lifecycle_strategic: 0.87 avg score (8 uses)
```

## 🚀 Deployment

### Local Testing
```bash
python enhanced_gradio_lab.py
# Access at http://localhost:7860
```

### Railway Deployment
```bash
# Add to requirements.txt
echo "gradio==4.44.0" >> requirements.txt
echo "PyPDF2==3.0.1" >> requirements.txt

# Deploy
railway up
```

### Share with Founder
The interface automatically creates a shareable link:
```
Running on public URL: https://xxxxx.gradio.live
```

## 🔑 Key Benefits

1. **Faster Iteration** - Test configurations in minutes
2. **Learning System** - Gets better with each run
3. **Objective Quality** - Automated scoring removes bias
4. **Proven Templates** - Reuse what works
5. **Focus Resources** - Process only relevant trends

## 📝 Notes

- All data stored locally in SQLite databases
- Examples and templates persist between sessions
- Quality thresholds customizable in each module
- Can export/import template libraries

## 🎉 Result

With these enhancements, your pipeline:
- **Learns** from successful runs
- **Filters** irrelevant trends
- **Scores** quality automatically
- **Reuses** proven templates
- **Improves** over time

Transform your pipeline from "trying different prompts" to "systematically discovering what works"!
# 2. System Overview

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (Developer)                         │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ Command: python run_pipeline.py --input X --brand Y
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     run_pipeline.py (CLI)                        │
│                                                                  │
│  - Parse arguments                                               │
│  - Load input document & brand profile                           │
│  - Create output directory                                       │
│  - Initialize logging                                            │
│  - Execute LangChain SequentialChain                             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              LangChain SequentialChain                           │
│                                                                  │
│  Stage 1: Input Processing        (LLMChain)                    │
│           ↓                                                      │
│  Stage 2: Signal Amplification    (LLMChain)                    │
│           ↓                                                      │
│  Stage 3: General Translation     (LLMChain)                    │
│           ↓                                                      │
│  Stage 4: Brand Contextualization (LLMChain + Research Data)    │
│           ↓                                                      │
│  Stage 5: Opportunity Generation  (LLMChain + Jinja2)           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ├──────────────────┐
                  │                  │
                  ▼                  ▼
          ┌──────────────┐   ┌──────────────┐
          │  OpenRouter  │   │ File System  │
          │     API      │   │   Storage    │
          │              │   │              │
          │ Claude Sonnet│   │ Intermediate │
          │     4.5      │   │   Outputs    │
          └──────────────┘   └──────────────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │   Results    │
                              │              │
                              │ 5 Opportunity│
                              │    Cards     │
                              └──────────────┘
```

## 2.2 Data Flow

```
INPUT DOCUMENT (PDF)
    ↓
[STAGE 1: Input Processing]
    → stage1/inspiration-analysis.md
    ↓
[STAGE 2: Signal Amplification]
    → stage2/trend-analysis.md
    ↓
[STAGE 3: General Translation]
    → stage3/universal-lessons.md
    ↓
[STAGE 4: Brand Contextualization] ← BRAND PROFILE (YAML)
    → stage4/brand-contextualization.md  ← RESEARCH DATA (Local Files)
    ↓
[STAGE 5: Opportunity Generation]
    → stage5/opportunity-1.md
    → stage5/opportunity-2.md
    → stage5/opportunity-3.md
    → stage5/opportunity-4.md
    → stage5/opportunity-5.md
    → stage5/opportunities-summary.md
```

---

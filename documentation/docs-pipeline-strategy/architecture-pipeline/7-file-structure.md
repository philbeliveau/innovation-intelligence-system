# 7. File Structure

## 7.1 Complete Repository Layout

```
innovation-intelligence-system/
├── .env                                # Environment variables (API keys)
├── .env.template                       # Template for environment setup
├── .gitignore                          # Git ignore rules
├── README.md                           # Setup and usage instructions
├── requirements.txt                    # Python dependencies
├── run_pipeline.py                     # Main CLI execution script
│
├── pipeline/                           # Pipeline implementation
│   ├── __init__.py
│   ├── chains.py                       # SequentialChain setup
│   ├── utils.py                        # Helper functions
│   │
│   ├── stages/                         # Stage implementations
│   │   ├── __init__.py
│   │   ├── stage1_input_processing.py
│   │   ├── stage2_signal_amplification.py
│   │   ├── stage3_general_translation.py
│   │   ├── stage4_brand_contextualization.py
│   │   └── stage5_opportunity_generation.py
│   │
│   └── prompts/                        # PromptTemplate definitions
│       ├── __init__.py
│       ├── stage1_prompt.py
│       ├── stage2_prompt.py
│       ├── stage3_prompt.py
│       ├── stage4_prompt.py
│       └── stage5_prompt.py
│
├── templates/                          # Jinja2 templates
│   └── opportunity-card.md.j2          # Opportunity card markdown template
│
├── data/                               # All data files (NOT committed to git)
│   ├── input-manifest.yaml             # Input document registry
│   ├── brand-profiles/                 # Brand YAML files
│   │   ├── lactalis-canada.yaml
│   │   ├── mccormick-usa.yaml
│   │   ├── columbia-sportswear.yaml
│   │   └── decathlon.yaml
│   │
│   └── test-outputs/                   # Test execution results
│       ├── {input-id}-{brand-id}-{timestamp}/
│       │   ├── logs/
│       │   │   ├── pipeline.log
│       │   │   └── errors.log
│       │   ├── stage1/
│       │   │   └── inspiration-analysis.md
│       │   ├── stage2/
│       │   │   └── trend-analysis.md
│       │   ├── stage3/
│       │   │   └── universal-lessons.md
│       │   ├── stage4/
│       │   │   └── brand-contextualization.md
│       │   └── stage5/
│       │       ├── opportunity-1.md
│       │       ├── opportunity-2.md
│       │       ├── opportunity-3.md
│       │       ├── opportunity-4.md
│       │       ├── opportunity-5.md
│       │       └── opportunities-summary.md
│
├── documentation/                      # Input documents + research
│   ├── document/                       # Test input PDFs
│   │   ├── savannah-bananas.pdf
│   │   ├── premium-fast-food-trend.pdf
│   │   ├── combined-trends-nonalcoholic-sacred-sync.pdf
│   │   ├── cat-dad-campaign.pdf
│   │   └── qr-garment-resale.pdf
│   │
│   └── innovation-research/            # TRIZ/SIT/SPECTRE frameworks (reference only)
│
├── docs/                               # Documentation
│   ├── architecture.md                 # This document
│   ├── prd.md                          # Product requirements
│   ├── brand-profile-schema.md         # Brand YAML documentation
│   ├── opportunity-card-format.md      # Opportunity card spec
│   ├── stage-1-3-quality-checklist.md  # Manual review checklist
│   ├── differentiation-rubric.md       # Brand comparison scoring
│   ├── opportunity-quality-rubric.md   # Final quality assessment
│   │
│   └── web-search-setup/               # Pre-existing brand research data
│       ├── lactalis-canada-research.md       # 545 lines, 8 sections, 46 subsections
│       ├── mccormick-usa-research.md         # 720 lines, 8 sections, 46 subsections
│       ├── columbia-sportswear-research.md   # 574 lines, 8 sections, 46 subsections
│       ├── decathlon-research.md             # 603 lines, 8 sections, 46 subsections
│       └── brand-research-agent-prompt.md    # Research methodology template
│
└── tests/                              # Test scripts
    ├── test_input_loading.py           # Validate input documents load
    ├── test_brand_profiles.py          # Validate brand YAML syntax
    ├── test_stage.py                   # Test individual stages
    ├── test_stages_1_3.py              # Integration test Stages 1-3
    └── test_stage4_differentiation.py  # Multi-brand comparison test
```

## 7.2 Output Directory Naming Convention

```
data/test-outputs/{input-id}-{brand-id}-{timestamp}/

Example:
data/test-outputs/savannah-bananas-lactalis-20251007-142345/
```

**Rationale:** Timestamp ensures unique directories for re-runs, input-brand prefix enables easy filtering.

---

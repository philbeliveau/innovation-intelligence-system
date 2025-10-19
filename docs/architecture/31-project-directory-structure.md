# 3.1 Project Directory Structure

```
innovation-web/
├── app/
│   ├── api/
│   │   ├── analyze-document/
│   │   │   └── route.ts          # LLM document analysis
│   │   ├── onboarding/
│   │   │   ├── current-company/
│   │   │   │   └── route.ts      # Get current company from cookie
│   │   │   └── set-company/
│   │   │       └── route.ts      # Set company cookie
│   │   ├── run/
│   │   │   └── route.ts          # Execute pipeline
│   │   ├── status/
│   │   │   └── [runId]/
│   │   │       └── route.ts      # Poll pipeline status
│   │   └── upload/
│   │       └── route.ts          # Upload to Vercel Blob
│   ├── analyze/
│   │   └── [uploadId]/
│   │       └── page.tsx          # Intermediary card page
│   ├── onboarding/
│   │   └── page.tsx              # Company selection
│   ├── pipeline/
│   │   └── [runId]/
│   │       └── page.tsx          # Pipeline viewer
│   ├── results/
│   │   └── [runId]/
│   │       └── page.tsx          # Results display
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Homepage (upload)
├── components/
│   ├── ui/                       # shadcn/ui components
│   │   ├── badge.tsx
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── select.tsx
│   │   └── skeleton.tsx
│   ├── CompanyBadge.tsx          # Display company name
│   ├── FileUploadZone.tsx        # Drag & drop upload
│   ├── InspirationTrack.tsx      # Stage 1 inspiration card
│   ├── LeftSidebar.tsx           # Collapsible home menu
│   └── StageBox.tsx              # Stages 2-5 status box
├── lib/
│   └── utils.ts                  # Utility functions
├── public/
│   └── images/                   # Static images
├── .env.local                    # Environment variables
├── .env.example                  # Environment template
├── next.config.js
├── package.json
├── tailwind.config.ts
└── tsconfig.json

# Python Pipeline (existing, unchanged)
pipeline/
├── stages/
│   ├── stage1_input_processing.py
│   ├── stage2_signal_amplification.py
│   ├── stage3_general_translation.py
│   ├── stage4_brand_contextualization.py
│   └── stage5_opportunity_generation.py
├── utils.py
└── chains.py

scripts/
└── run_pipeline.py               # Entry point (modified)

data/
├── brand-profiles/               # YAML files
├── brand-research/               # Markdown files
└── test-outputs/                 # Pipeline outputs
    └── {run_id}/
        ├── logs/
        │   └── pipeline.log
        ├── stage1/
        │   ├── inspiration-analysis.md
        │   └── inspirations.json
        ├── stage2/
        ├── stage3/
        ├── stage4/
        └── stage5/
            ├── opportunity-1.md
            ├── opportunity-2.md
            ├── opportunity-3.md
            ├── opportunity-4.md
            └── opportunity-5.md
```

---

# 3. Product Overview

## 3.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Vercel)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Onboarding│→│ Homepage │→│Intermediary│→│Pipeline  │→│Results││
│  │(Company) │  │(Upload)  │  │  Card    │  │  View    │  │(Opp.)││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
           ↓                    ↓            ↓           ↓
┌─────────────────────────────────────────────────────────────┐
│                      API Routes (Next.js)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ /upload  │  │ /analyze │  │  /run    │  │ /status  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
           ↓                    ↓
┌─────────────────────────────────────────────────────────────┐
│              External Services & Pipeline                   │
│  ┌─────────────────┐         ┌─────────────────────────┐  │
│  │ Vercel Blob     │         │ Python Pipeline         │  │
│  │ (File Storage)  │         │ (Background Process)    │  │
│  └─────────────────┘         └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3.2 Core User Flow

1. **Onboarding** → User arrives at "My Board of Ideators" page, types company name (Lactalis, Columbia, Decathlon, McCormick)
2. **Company Loaded** → System validates and loads brand profile from YAML, redirects to upload page
3. **Upload** → Drag & drop PDF, file uploads to Vercel Blob
4. **Analyze** → LLM extracts document summary, industry, theme, and ideation tracks
5. **Review** → View intermediary card with analysis results and 2 selected tracks
6. **Launch** → Click "Launch" button to start horizontal pipeline execution
7. **Watch** → See real-time progress through 5 stages flowing left-to-right
8. **Review** → View 5 generated opportunity cards on results page
9. **Action** → Download opportunities or start new pipeline run

---

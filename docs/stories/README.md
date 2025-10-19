# Innovation Intelligence Web App - User Stories

This directory contains all user stories for the Innovation Intelligence Web App hackathon implementation.

---

## Epic Overview

### **Epic 1: Core Upload & File Management** ✅ Ready for Implementation

**Status:** Ready for Development
**Priority:** P0 (Critical Path)
**Estimated Time:** 4 hours
**Dependencies:** Vercel account, brand profile YAMLs

**Goal:** Build web-based onboarding and file upload interface that enables users to select company context and upload market signal documents.

**Document:** [Epic 1 Overview](./epic-1-overview.md)

---

## Stories

### **Story 1.1: Landing Page with Company Selection**

**Priority:** P0
**Estimated Time:** 1.5 hours
**Dependencies:** None
**Status:** Ready for Implementation

**Summary:** Create root route (`/`) as combined onboarding/landing page with "My Board of Ideators" design. User types company name, system validates against brand profiles, saves to cookie, and redirects.

**Key Deliverables:**
- Landing page UI with circular colored design
- Company name input with validation
- API route for brand profile loading
- Cookie-based session management

**Document:** [Story 1.1 Details](./epic-1-story-1.1.md)

---

### **Story 1.2: File Upload to Vercel Blob**

**Priority:** P0
**Estimated Time:** 1 hour
**Dependencies:** Vercel account, Blob storage token
**Status:** Ready for Implementation

**Summary:** Implement Vercel Blob integration with multipart file upload endpoint. Accept PDF/TXT/MD files up to 25MB, store in Blob, return URL and metadata.

**Key Deliverables:**
- `POST /api/upload` endpoint
- File type and size validation
- Vercel Blob SDK integration
- Retry logic with exponential backoff

**Document:** [Story 1.2 Details](./epic-1-story-1.2.md)

---

### **Story 1.3: Upload Page UI with Company Badge**

**Priority:** P0
**Estimated Time:** 1.5 hours
**Dependencies:** Story 1.1 (cookie), Story 1.2 (API)
**Status:** Ready for Implementation

**Summary:** Build `/upload` page with drag & drop zone, company badge, and upload progress. On success, save blob URL to sessionStorage and redirect to analysis page.

**Key Deliverables:**
- Upload page UI with drag & drop
- Company badge from cookie
- Upload progress tracking
- SessionStorage integration

**Document:** [Story 1.3 Details](./epic-1-story-1.3.md)

---

## Implementation Order

Stories must be completed **in sequence** for Epic 1:

1. **Story 1.1** → Establishes company context via cookie
2. **Story 1.2** → Enables file storage via Vercel Blob API
3. **Story 1.3** → Connects user flow (reads cookie, calls API, redirects)

**Critical Path:** All three stories required for functional upload flow.

---

## Quick Start Guide

### Prerequisites

```bash
# Install Node.js 20+
node --version  # Should be 20.x or higher

# Install dependencies
npm install

# Install additional packages for Epic 1
npm install @vercel/blob react-dropzone yaml
npx shadcn-ui@latest add badge progress card
```

### Environment Setup

Create `.env.local`:
```bash
# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_...  # Get from Vercel dashboard

# Optional: LLM configuration (for Epic 2+)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=anthropic/claude-sonnet-4.5
```

### Development Workflow

```bash
# Start dev server
npm run dev

# Open browser
open http://localhost:3000

# Run tests (when available)
npm test
```

---

## Testing Strategy

### Manual Testing Checklist (Epic 1)

#### Story 1.1
- [ ] Type "lactalis" on landing page → redirects to `/upload`
- [ ] Type "invalid" → shows error message
- [ ] Cookie persists after page refresh

#### Story 1.2
- [ ] Upload 5MB PDF → returns blob URL in < 5 seconds
- [ ] Upload 30MB file → returns 400 error
- [ ] Upload .exe file → returns 400 error

#### Story 1.3
- [ ] Visit `/upload` without cookie → redirects to `/`
- [ ] Drag & drop PDF → shows progress → redirects to `/analyze/{uploadId}`
- [ ] Check sessionStorage → `upload_{uploadId}` contains blob URL

### CLI Regression Testing

```bash
# Verify existing Python pipeline still works
python scripts/run_pipeline.py \
  --brand lactalis-canada \
  --input data/test-inputs/savannah-bananas.pdf

# Expected: Pipeline executes successfully, no errors
```

---

## File Structure

```
docs/stories/
├── README.md                    # This file
├── epic-1-overview.md           # Epic 1 summary
├── epic-1-story-1.1.md          # Landing page story
├── epic-1-story-1.2.md          # Upload API story
└── epic-1-story-1.3.md          # Upload UI story
```

---

## Related Documentation

- **PRD:** `/docs/prd.md` - Full product requirements
- **Architecture:** `/docs/architecture-hackathon-web-app.md` (if exists)
- **Visual Reference:** `/docs/image/Landing-page.png`, `/docs/image/main-page.png`
- **Brand Profiles:** `/data/brand-profiles/*.yaml`
- **Test Data:** `/data/test-inputs/savannah-bananas.pdf`

---

## Definition of Done (Epic 1)

Epic 1 is complete when:

- [x] All 3 stories meet their acceptance criteria
- [x] End-to-end flow works: `/` → type company → `/upload` → upload file → redirect to `/analyze/{uploadId}`
- [x] Company context persists across navigation (cookie)
- [x] File uploads successfully to Vercel Blob
- [x] Blob URL saved to sessionStorage
- [x] UI matches reference designs (90%+ similarity)
- [x] No console errors or TypeScript compilation errors
- [x] Existing Python CLI pipeline still works unchanged
- [x] Manual testing completed for all 4 brands

---

## Support & Questions

**Project Owner:** Philippe Beliveau
**Created:** 2025-10-19
**Last Updated:** 2025-10-19

For questions or issues:
1. Review story documents for detailed requirements
2. Check PRD for business context
3. Test with CLI to verify Python pipeline integrity

---

## Epic 3: Pipeline Integration (Phase 4-5) ✅ Ready for Implementation

**Status:** Ready for Development
**Priority:** P0 (Critical Path)
**Estimated Time:** 4.5 hours
**Dependencies:** Stories 1.2 (Blob API), Python pipeline

**Goal:** Connect Next.js web application to existing Python 5-stage LLM pipeline, enabling background execution from uploaded files with real-time status monitoring.

---

### **Story 3.1: API Routes for Pipeline Execution**

**Priority:** P0
**Estimated Time:** 2 hours
**Dependencies:** None
**Status:** Ready for Implementation

**Summary:** Create `/api/run`, `/api/status/[runId]`, and `/api/analyze-document` endpoints that trigger Python subprocess execution, poll log files for status, and extract document metadata using LLM.

**Key Deliverables:**
- POST `/api/run` - Triggers pipeline execution in background
- GET `/api/status/[runId]` - Returns current stage and Stage 1 track data
- POST `/api/analyze-document` - LLM extracts document summary/metadata
- Onboarding API routes for company cookie management

**Document:** [Story 3.1 Details](./epic-3-story-3.1-api-routes.md)

---

### **Story 3.2: Python Pipeline Modifications for Web Interface**

**Priority:** P0
**Estimated Time:** 1 hour
**Dependencies:** None (can run parallel with Story 3.1)
**Status:** Ready for Implementation

**Summary:** Add `--input-file` and `--run-id` CLI arguments, implement `run_from_uploaded_file()` function, modify Stage 1 to output `inspirations.json` with structured track data, and update Stage 1 prompt to extract exactly 2 tracks.

**Key Deliverables:**
- New CLI arguments: `--input-file`, `--run-id`
- New execution function: `run_from_uploaded_file()`
- Stage 1 JSON output: `inspirations.json`
- Updated Stage 1 prompt for exactly 2 tracks

**Document:** [Story 3.2 Details](./epic-3-story-3.2-python-modifications.md)

---

### **Story 3.3: Status Polling and Monitoring**

**Priority:** P0
**Estimated Time:** 1.5 hours
**Dependencies:** Story 3.1 (requires `/api/status` endpoint)
**Status:** Ready for Implementation

**Summary:** Implement frontend polling mechanism (5-second intervals), horizontal pipeline viewer UI with stage boxes, Stage 1 track card display, and real-time status updates.

**Key Deliverables:**
- Pipeline viewer page: `app/pipeline/[runId]/page.tsx`
- Polling mechanism with 5-second intervals
- Horizontal stage boxes with status icons
- Stage 1 track cards matching reference design

**Document:** [Story 3.3 Details](./epic-3-story-3.3-status-polling.md)

---

## Implementation Order (Epic 3)

**Recommended sequence:**

1. **Story 3.2** (1 hour) - Python modifications first (prerequisite for API testing)
2. **Story 3.1** (2 hours) - API routes (test with new CLI args)
3. **Story 3.3** (1.5 hours) - Frontend polling (requires `/api/status` endpoint)

Stories 3.1 and 3.2 can run in parallel if multiple developers available.

---

## Future Epics (Coming Soon)

- **Epic 2:** Document Analysis & Intermediary Card
- **Epic 4:** Pipeline Viewer & Results Display

---

## Definition of Done (Epic 3)

Epic 3 is complete when:

- [x] All 3 stories meet their acceptance criteria
- [x] Web-triggered pipeline run completes all 5 stages successfully
- [x] Real-time status updates visible in browser (5-second polling)
- [x] Stage 1 track cards display correctly with JSON data
- [x] Existing CLI pipeline execution (`--batch`) works without regression
- [x] Error handling tested (corrupted PDF, missing brand, network failures)
- [x] Manual E2E test passes: upload → analyze → launch → monitor → results
- [x] No memory leaks (polling cleanup verified)
- [x] Python subprocess execution verified on Vercel deployment

---

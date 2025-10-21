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
**Status:** Complete (Modified by Story 1.4)

**Summary:** Build `/upload` page with drag & drop zone, company badge, and upload progress. ~~On success, save blob URL to sessionStorage and redirect to analysis page.~~ **Modified by Story 1.4:** User stays on page after upload to enable upload history feature.

**Key Deliverables:**
- Upload page UI with drag & drop
- Company badge from cookie
- Upload progress tracking
- SessionStorage integration
- **Modified:** No automatic redirect (Story 1.4)

**Document:** [Story 1.3 Details](./1.3.upload-page-ui-company-badge.md)

---

### **Story 1.4: Upload History Display with Card Navigation**

**Priority:** P2
**Estimated Time:** 1.5-2 hours
**Dependencies:** Story 1.1 (cookie), Story 1.2 (API), Story 1.3 (upload page)
**Status:** Ready for Implementation

**Summary:** Display previously uploaded documents as coral/pink gradient cards below the upload zone. User stays on `/upload` page after successful upload instead of automatic redirect. Upload history persists in localStorage (company-scoped) with max 20 uploads per company.

**Key Deliverables:**
- Remove automatic redirect from Story 1.3
- LocalStorage utility functions for upload history
- UploadHistorySection component with "or Select a Starting Points" heading
- UploadHistoryCard component with gradient design
- Card navigation to `/analyze/{uploadId}`
- Company filtering and FIFO limit enforcement

**Document:** [Story 1.4 Details](./1.4.upload-history-card-navigation.md)

---

## Implementation Order

Stories must be completed **in sequence** for Epic 1:

1. **Story 1.1** → Establishes company context via cookie
2. **Story 1.2** → Enables file storage via Vercel Blob API
3. **Story 1.3** → Connects user flow (reads cookie, calls API) ✅ Complete
4. **Story 1.4** → Adds upload history and multi-upload workflow (optional enhancement)

**Critical Path:** Stories 1.1-1.3 required for functional upload flow. Story 1.4 is optional P2 enhancement.

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
- [ ] Drag & drop PDF → shows progress → ~~redirects to `/analyze/{uploadId}`~~ stays on page (Story 1.4)
- [ ] Check sessionStorage → `upload_{uploadId}` contains blob URL

#### Story 1.4
- [ ] Upload file → stays on `/upload` page (no redirect)
- [ ] "or Select a Starting Points" section appears
- [ ] Upload history card displays with filename and timestamp
- [ ] Click history card → navigates to `/analyze/{uploadId}`
- [ ] Check localStorage → `upload_history_{company_id}` contains upload array
- [ ] Upload 21st file → oldest upload removed (20-limit enforced)
- [ ] Switch company → history filters to new company's uploads

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

- [x] All 3 stories (1.1-1.3) meet their acceptance criteria
- [x] End-to-end flow works: `/` → type company → `/upload` → upload file → ~~redirect to `/analyze/{uploadId}`~~ stay on page (Story 1.4)
- [x] Company context persists across navigation (cookie)
- [x] File uploads successfully to Vercel Blob
- [x] Blob URL saved to sessionStorage
- [x] UI matches reference designs (90%+ similarity)
- [x] No console errors or TypeScript compilation errors
- [x] Existing Python CLI pipeline still works unchanged
- [x] Manual testing completed for all 4 brands

**Story 1.4 Complete (Optional Enhancement) when:**
- [ ] Upload history cards display below upload zone
- [ ] User stays on `/upload` after successful upload
- [ ] History persists in localStorage (company-scoped)
- [ ] Click history card navigates to `/analyze/{uploadId}`
- [ ] 20-upload limit enforced (FIFO)
- [ ] Empty state handled (section hidden when no history)

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

---

## Epic 5: Backend Migration to Railway ⚙️ Ready for Implementation

**Status:** Ready for Development
**Priority:** P1 (Infrastructure Improvement)
**Estimated Time:** 9-12 hours
**Dependencies:** Stories 1.2 (Blob API), 3.1 (API routes), Railway account

**Goal:** Migrate Python pipeline execution from Vercel serverless functions to dedicated Railway backend, enabling scalable processing and decoupling frontend from backend infrastructure.

**Document:** [Epic 5 Overview](#epic-5-overview)

---

### **Story 5.1: FastAPI Backend Directory Structure**

**Priority:** P1
**Estimated Time:** 2-3 hours
**Dependencies:** None
**Status:** Ready for Implementation

**Summary:** Create minimal FastAPI backend at root level (`/backend`) with pipeline code copied from `/pipeline`, basic API endpoints, and local development setup.

**Key Deliverables:**
- `/backend` directory structure
- FastAPI app with `/run`, `/status`, `/health` endpoints
- Copy pipeline stages and prompts
- Requirements.txt with dependencies
- Local development with uvicorn

**Document:** [Story 5.1 Details](./5.1.fastapi-backend-structure.md)

---

### **Story 5.2: Railway Deployment Configuration**

**Priority:** P1
**Estimated Time:** 2-3 hours
**Dependencies:** Story 5.1 (backend structure)
**Status:** Ready for Implementation

**Summary:** Create Dockerfile and railway.json for Railway deployment, configure environment variables, deploy to Railway, and verify health checks work.

**Key Deliverables:**
- Dockerfile with single-stage build
- railway.json deployment config
- Railway project setup
- CORS configuration for Vercel
- Public URL endpoint

**Document:** [Story 5.2 Details](./5.2.railway-deployment-configuration.md)

---

### **Story 5.3: Frontend Migration to Railway Backend**

**Priority:** P1
**Estimated Time:** 2 hours
**Dependencies:** Story 5.2 (Railway deployment), Story 3.1 (API routes)
**Status:** Ready for Implementation

**Summary:** Refactor Next.js API routes to call Railway backend instead of local `execFile()`, create backend client utility, and test end-to-end flow.

**Key Deliverables:**
- Backend API client utility (`lib/backend-client.ts`)
- Refactored `/api/run` route (fetch instead of execFile)
- Refactored `/api/status` route (proxy to Railway)
- Environment variable configuration
- E2E testing

**Document:** [Story 5.3 Details](./5.3.frontend-railway-migration.md)

---

### **Story 5.4: Pipeline Execution Endpoints Implementation**

**Priority:** P0
**Estimated Time:** 3-4 hours
**Dependencies:** Story 5.1 (backend structure), Story 5.2 (Railway deployed), Story 5.3 (frontend connected)
**Status:** Ready for Implementation

**Summary:** Implement actual pipeline execution logic in FastAPI `/run` and `/status/{run_id}` endpoints, including PDF download from Vercel Blob, background pipeline execution with threading, and real-time status tracking.

**Key Deliverables:**
- POST `/run` endpoint with blob download and pipeline execution
- GET `/status/{run_id}` endpoint with live stage tracking
- Background threading for non-blocking execution
- Copy brand profiles to `/backend/data/brand-profiles/`
- Status file tracking (`/tmp/runs/{run_id}/status.json`)
- Stage 1 track data in status response

**Document:** [Story 5.4 Details](./5.4.pipeline-execution-endpoints.md)

---

## Implementation Order (Epic 5)

**Recommended sequence:**

1. **Story 5.1** (2-3 hours) - Create backend structure and test locally
2. **Story 5.2** (2-3 hours) - Deploy to Railway and verify health
3. **Story 5.3** (2 hours) - Connect frontend to Railway backend
4. **Story 5.4** (3-4 hours) - Implement pipeline execution logic

**Critical Path:** Stories must be completed sequentially (5.1 → 5.2 → 5.3 → 5.4)

**Total Epic Time:** 9-12 hours

---

---

## Epic 6: User Authentication & Session Management ✅ Complete

**Status:** Complete
**Priority:** P1 (Security & Foundation)
**Estimated Time:** 2 hours
**Dependencies:** Epic 1 (Upload flow), Epic 3 (Pipeline execution)

**Goal:** Integrate Clerk authentication to enable user sign-in, protected routes, and user identity tracking for future multi-user features.

---

### **Story 6.1: Clerk Authentication Integration**

**Priority:** P1
**Estimated Time:** 2 hours
**Dependencies:** None
**Status:** ✅ Complete

**Summary:** Integrate Clerk authentication with modal sign-in, protected routes for pipeline/results pages, and user profile UI in left sidebar. Public routes (landing, upload) remain accessible without authentication.

**Key Deliverables:**
- Clerk SDK installed and configured
- Middleware with route protection
- ClerkProvider in app layout
- Sign-in/UserButton in left sidebar
- Protected routes: `/pipeline/*`, `/results/*`, `/analyze/*`, `/api/run`, `/api/status/*`
- Public routes: `/`, `/upload`, `/api/upload`, `/api/onboarding/*`

**Document:** [Story 6.1 Details](./epic-6-story-6.1-clerk-authentication.md)

**Integration Impact:**
- ✅ **No breaking changes** to existing features
- ✅ Upload flow remains unauthenticated (public)
- ✅ Pipeline execution requires sign-in (protected)
- ✅ Foundation for Epic 7+ (user dashboards, saved runs, team collaboration)

---

## Future Epics (Coming Soon)

- **Epic 2:** Document Analysis & Intermediary Card
- **Epic 4:** Pipeline Viewer & Results Display
- **Epic 7:** User Dashboard & Saved Runs (links pipeline runs to Clerk user ID)
- **Epic 8:** Team Collaboration (share runs, comments, workspaces)

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

## Definition of Done (Epic 5)

Epic 5 is complete when:

- [ ] All 4 stories (5.1-5.4) meet their acceptance criteria
- [ ] Backend deployed to Railway with public URL
- [ ] Frontend successfully calls Railway backend (no local execFile)
- [ ] Pipeline executes all 5 stages on Railway infrastructure
- [ ] Health check endpoint returns 200 on Railway
- [ ] E2E flow works: Upload → Railway backend → Pipeline execution → Status polling → Results
- [ ] CORS configured correctly (Vercel can call Railway)
- [ ] Environment variables set in both Vercel and Railway
- [ ] Local development works with Dockerized backend
- [ ] Status tracking updates in real-time (5-second polling)
- [ ] Stage 1 tracks display correctly in frontend
- [ ] All 4 brand profiles tested (lactalis, kind, hidden-valley, mccormick)
- [ ] Error handling tested (invalid blob, corrupted PDF, LLM failures)
- [ ] No regression: Existing features still work (upload, status, results)
- [ ] Documentation updated (README, DEPLOYMENT.md)
- [ ] Background execution doesn't block API (concurrent runs work)

---

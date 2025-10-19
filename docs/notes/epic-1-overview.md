# Epic 1: Core Upload & File Management - Brownfield Enhancement

**Status:** Ready for Implementation
**Priority:** P0 (Hackathon Critical Path)
**Estimated Time:** 4 hours
**Dependencies:** Vercel account, brand profile YAMLs

---

## Epic Goal

Build a web-based onboarding and file upload interface for the Innovation Intelligence Pipeline that enables users to select their company context and upload market signal documents (PDFs, trend reports), establishing the foundation for the web application's user flow.

---

## Epic Description

### Existing System Context

- **Current relevant functionality:** CLI-based Python pipeline (`scripts/run_pipeline.py`) that processes market signals and generates brand-specific opportunities. Operates entirely via command-line arguments with brand profiles stored in `/data/brand-profiles/*.yaml`
- **Technology stack:** Python 3.10+, LangChain 0.1.x, YAML-based brand profiles (4 brands: lactalis-canada, mccormick-usa, columbia-sportswear, decathlon)
- **Integration points:**
  - Brand profile YAML files in `/data/brand-profiles/`
  - Pipeline expects file path + brand ID as input
  - No existing web interface or HTTP endpoints

### Enhancement Details

**What's being added/changed:**
- Next.js 15 web application with TypeScript + Tailwind CSS
- Combined onboarding/landing page at root (`/`) with "My Board of Ideators" design featuring circular layout and company name input
- File upload functionality using Vercel Blob storage with drag & drop interface
- Company context management via HTTP-only cookies (7-day expiry)
- Frontend route structure: `/` (onboarding/landing) → `/upload` (file upload)

**How it integrates:**
- Brand profiles remain in existing YAML format (no changes to data structure)
- Uploaded files stored in Vercel Blob, with URLs passed to existing Python pipeline
- Company selection loads existing YAML files server-side via Next.js API routes
- No modifications to Python pipeline in this epic (integration deferred to Epic 3)

**Success criteria:**
- ✅ User can type company name on landing page and access brand-specific upload interface
- ✅ Valid company names (Lactalis, Columbia, Decathlon, McCormick) map to correct YAML files
- ✅ PDF/TXT/MD files upload successfully to Vercel Blob (< 5 seconds for 10MB)
- ✅ Company context persists across page navigation via cookie
- ✅ UI matches reference design `docs/image/Landing-page.png` and `docs/image/main-page.png`

---

## Stories

### **Story 1.1: Landing Page with Company Selection**

**Description:** Create the root route (`/`) as a combined onboarding/landing page with "My Board of Ideators" design. User types company name (Lactalis, Columbia, Decathlon, McCormick), system validates against existing brand profiles, saves company ID to cookie, and redirects to upload page.

**Key Requirements:**
- 8 colored circles (teal, blue, yellow, orange) in circular pattern
- Central text input with placeholder: "Lactalis, Columbia, Decathlon, McCormick..."
- Top navigation tabs (Everything, Spaces, Serendipity) - visual only
- Case-insensitive company name matching
- API route: `POST /api/onboarding/set-company` loads YAML and sets cookie

**Estimated Time:** 1.5 hours

**Document:** [Story 1.1 Details](./epic-1-story-1.1.md)

---

### **Story 1.2: File Upload to Vercel Blob**

**Description:** Implement Vercel Blob integration with multipart file upload endpoint. Accept PDF/TXT/MD files up to 25MB, store in public Blob storage, return blob URL and upload metadata. Handle validation errors (file type, size limits).

**Key Requirements:**
- API route: `POST /api/upload` with multipart/form-data
- Vercel Blob SDK integration (`@vercel/blob`)
- File type validation (PDF, TXT, MD only)
- Return blob URL, file name, size, timestamp
- Generate unique upload ID: `upload-{timestamp}`

**Estimated Time:** 1 hour

**Document:** [Story 1.2 Details](./epic-1-story-1.2.md)

---

### **Story 1.3: Upload Page UI with Company Badge**

**Description:** Build `/upload` page with drag & drop file upload zone, company badge displaying selected brand (from cookie), and automatic redirect to analysis page after upload. On successful upload, redirect to `/analyze/{uploadId}` for document analysis (implementation deferred to Epic 2).

**Key Requirements:**
- Check cookie for company context, redirect to `/` if missing
- Drag & drop zone using `react-dropzone`
- Display company name badge (shadcn/ui Badge component)
- Show upload progress bar during file transfer
- Save `blob_url` to sessionStorage keyed by `upload_id`
- Match reference design `docs/image/main-page.png`

**Estimated Time:** 1.5 hours

**Document:** [Story 1.3 Details](./epic-1-story-1.3.md)

---

## Compatibility Requirements

- [x] **Existing APIs remain unchanged** - No Python pipeline modifications in this epic
- [x] **Database schema changes are backward compatible** - No database (file-based storage)
- [x] **UI changes follow existing patterns** - New Next.js app follows modern React patterns
- [x] **Performance impact is minimal** - Client-side only, no impact on Python pipeline

---

## Risk Mitigation

### Primary Risk: Vercel Blob upload failures blocking user flow

**Mitigation:**
- Implement retry logic (3 attempts with exponential backoff)
- Add fallback to save files in `/tmp` if Blob unavailable
- Display clear error messages with retry option

**Rollback Plan:**
- All changes are in new Next.js app directory (no existing code modified)
- Remove deployment from Vercel, revert to CLI-only usage
- Brand profile YAML files unchanged, pipeline continues working via CLI

---

## Definition of Done

- [x] All stories completed with acceptance criteria met
- [x] Existing functionality verified through testing - Python pipeline runs unchanged via CLI
- [x] Integration points working correctly - YAML files load correctly from Next.js API routes
- [x] Documentation updated appropriately - Update README with web app setup instructions
- [x] No regression in existing features - CLI pipeline execution remains fully functional

---

## Story Manager Handoff

**Story Manager Handoff:**

"Please develop detailed user stories for this brownfield epic. Key considerations:

- This is an enhancement to an existing system running **Python 3.10+ with LangChain 0.1.x** (CLI-based pipeline)
- Integration points:
  - `/data/brand-profiles/*.yaml` files (4 brands: lactalis-canada, mccormick-usa, columbia-sportswear, decathlon)
  - Vercel Blob storage API
  - HTTP-only cookies for session management
- Existing patterns to follow:
  - YAML brand profile structure (no modifications)
  - Python pipeline CLI interface remains unchanged
  - Standard Next.js 15 App Router patterns
- Critical compatibility requirements:
  - No modifications to Python pipeline code in this epic
  - Brand profile YAML files must remain readable by existing pipeline
  - CLI execution must continue working unchanged
- Each story must include verification that existing CLI functionality remains intact

The epic should maintain system integrity while delivering a web-based onboarding and file upload interface that prepares files for pipeline execution."

---

## Implementation Order

1. **Story 1.1** - Landing page establishes company context
2. **Story 1.2** - Upload API enables file storage
3. **Story 1.3** - Upload UI connects user flow

**Critical Path:** All three stories must be completed in sequence for Epic 1 to be functional.

---

## Testing Strategy

### Manual Testing Checklist

**Story 1.1:**
- [ ] Type "lactalis" → redirects to `/upload` with cookie set
- [ ] Type "invalid-company" → shows error message
- [ ] Cookie persists after browser refresh

**Story 1.2:**
- [ ] Upload 5MB PDF → returns blob URL in < 5 seconds
- [ ] Upload 30MB file → returns 400 error
- [ ] Upload .exe file → returns 400 error

**Story 1.3:**
- [ ] Visit `/upload` without cookie → redirects to `/`
- [ ] Drag & drop PDF → shows progress bar → redirects to `/analyze/{uploadId}`
- [ ] Click to upload TXT file → uploads successfully

### CLI Regression Testing

```bash
# Verify existing pipeline still works
python scripts/run_pipeline.py --brand lactalis-canada --input data/test-inputs/savannah-bananas.pdf
```

Expected: Pipeline executes successfully, generates outputs in `data/test-outputs/`

---

## Related Documents

- **PRD:** `/docs/prd.md` - Sections 4.0 (Onboarding), 4.1 (Upload Page), 4.5.2 (Upload API)
- **Architecture:** `/docs/architecture-hackathon-web-app.md` (if exists)
- **Visual Reference:** `/docs/image/Landing-page.png`, `/docs/image/main-page.png`
- **Brand Profiles:** `/data/brand-profiles/*.yaml`

---

**Epic Owner:** Philippe Beliveau
**Created:** 2025-10-19
**Last Updated:** 2025-10-19

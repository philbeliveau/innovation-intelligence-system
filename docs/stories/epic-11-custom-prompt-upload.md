# Epic 11: Custom Prompt Upload System - Brownfield Enhancement

## Epic Goal

Enable innovation teams (founders at Lactalis, McCormick, Decathlon) to customize LLM prompts for the 7-stage pipeline via file upload without writing code, allowing non-technical users to iterate on prompt strategies and track which prompt versions produce successful results.

## Epic Description

### Existing System Context

**Current Relevant Functionality:**
- Gradio UI at `backend/experimentation/gradio_lab.py` (1,518 lines, 95%+ test coverage)
- 7-stage pipeline (Stage 0-6) execution via Railway backend
- Hardcoded prompt templates at `backend/experimentation/prompts/*.md`
- PostgreSQL database with Experiment table for persistence
- FastAPI backend with `/run/local` endpoint for pipeline execution

**Technology Stack:**
- Frontend: Gradio 5.x (Python web UI framework)
- Backend: FastAPI + Python 3.11
- Database: PostgreSQL (via psycopg2 direct connection)
- LLM: Claude via OpenRouter API
- Deployment: Railway (backend) + HuggingFace Spaces (Gradio UI)

**Integration Points:**
- Gradio UI → FastAPI `/run/local` endpoint (httpx AsyncClient)
- Backend pipeline → Prompt template `.md` files (current: hardcoded, future: dynamic)
- Gradio UI → PostgreSQL Experiment table (save results with metadata)

### Enhancement Details

**What's Being Added/Changed:**

1. **Prompt Template Download:**
   - "Custom Prompts" tab in Gradio UI
   - Download buttons for 7 default `.md` templates (individual + ZIP)
   - README.md explaining placeholder requirements and customization examples

2. **Prompt File Upload:**
   - 7 file upload components (one per stage, optional)
   - Client-side validation for required placeholders (e.g., `{insights}`, `{brand_context}`)
   - Validation feedback UI showing per-stage status (✅ valid, ❌ missing placeholders, ℹ️ using default)

3. **Backend Custom Prompt Integration:**
   - Modify `/run/local` endpoint to accept `custom_prompts` field
   - Update 7 stage files to use uploaded prompt content instead of default `.md` files
   - Create `PromptFileValidator` class for server-side validation

4. **Database Traceability:**
   - Add `customPromptFiles` JSONB field to Experiment table
   - Store prompt file metadata (filename, hash, content) with each experiment
   - Display indicator in UI when custom prompts were used
   - "Download Custom Prompts" button to re-download exact prompts from past experiments

**How It Integrates:**
- Additive feature - does NOT break existing default prompt behavior
- When no custom prompts uploaded → pipeline uses existing hardcoded templates (backward compatible)
- When custom prompts uploaded → Gradio sends file content to backend via `custom_prompts` field
- Backend validates and uses custom prompt content for specified stages
- Results saved to database with full prompt traceability

**Success Criteria:**
- 50% of founders download default templates within first week
- 20% of pipeline runs use at least 1 custom prompt within first month
- <5% of custom prompt uploads fail validation (indicates good UX)
- Zero breaking changes to existing default prompt behavior
- 80% of "Good" tagged experiments use custom prompts (indicates feature value)

## Stories

### Story 11.6.1: Prompt Download, Upload & Validation UI (MVP Phase 1)

**Description:** Create Gradio UI components for downloading default prompt templates, uploading custom `.md` files (0-7 stages), and client-side validation with clear feedback.

**Acceptance Criteria:**
- New "📂 Custom Prompts" tab in Gradio UI
- Download section with 7 individual buttons + "Download ALL (ZIP)" button
- ZIP includes all 7 templates + README.md with placeholder documentation
- 7 file upload components (`gr.File(file_types=[".md"])`) labeled "Stage X Custom Prompt (optional)"
- "✅ Validate Uploaded Prompts" button triggering client-side validation
- Validation checks each uploaded file for required placeholders (e.g., Stage 4 must have `{insights}`, `{matched_techniques}`, `{brand_context}`, `{no_hallucination_rules}`)
- Validation results display per-stage status:
  - ✅ "Stage 4: Valid (stage_4_bold_v1.2.md)"
  - ❌ "Stage 4: MISSING placeholders: {insights}, {brand_context}"
  - ℹ️ "Stage 0: Using default prompt (no file uploaded)"
- File size limit enforced (max 1MB per file)
- Invalid files highlighted in red, blocking pipeline execution
- Uploaded files persist in `gr.State()` during session
- Help text: "Leave blank to use default prompt"

**Technical Notes:**
- Use `zipfile` module to create ZIP of default templates
- Use regex pattern matching to validate placeholder presence: `\{[a-z_]+\}`
- Store uploaded file content in `gr.State()` for pipeline execution
- Reference placeholder requirements table from handoff doc

**Test Coverage:**
- Unit tests for placeholder validation logic
- Integration test: upload valid file → validation passes → file content available for pipeline
- Integration test: upload file missing placeholders → validation fails → pipeline button disabled
- Edge case: upload `.txt` file renamed to `.md` → accept if content valid

**Estimated Effort:** 5 story points

---

### Story 11.6.2: Backend Custom Prompt Integration (MVP Phase 2)

**Description:** Modify FastAPI backend to accept `custom_prompts` field in `/run/local` endpoint and update 7 pipeline stage files to use uploaded prompt content instead of default `.md` templates.

**Acceptance Criteria:**
- `/run/local` endpoint accepts optional `custom_prompts` dict field:
  ```json
  {
    "report_text": "...",
    "brand_profile": {...},
    "custom_prompts": {
      "stage_0": "Brand enrichment prompt content...",
      "stage_4": "Custom concept generation prompt..."
    }
  }
  ```
- Create `backend/pipeline/prompt_file_validator.py` with `PromptFileValidator` class
- `PromptFileValidator.validate(stage, content)` checks for required placeholders server-side
- If validation fails → return 400 error with clear message ("Stage 4 missing {insights} placeholder")
- Modify 7 stage files (`stage0_brand_context.py` through `stage6_packaging.py`):
  - Add `custom_prompt_content: Optional[str]` parameter to `execute()` function
  - If `custom_prompt_content` provided → use it for prompt formatting
  - If `custom_prompt_content` is None → use default `.md` file (existing behavior)
- `pipeline_orchestrator.py` passes `custom_prompts` to each stage's `execute()` function
- Progress indicator in status endpoint shows "Using custom prompts: Stage 4"

**Technical Notes:**
- Backend validation uses same regex pattern as frontend (consistency)
- Custom prompt content should be stored in memory during pipeline execution (not persisted to `/tmp/runs/`)
- Ensure placeholder formatting works with uploaded content (e.g., `.format(**data)`)
- Default behavior unchanged: if `custom_prompts` field omitted → use existing templates

**Test Coverage:**
- Unit tests for `PromptFileValidator` (valid/invalid cases)
- Integration test: send request with `custom_prompts` → pipeline uses uploaded content
- Integration test: send request without `custom_prompts` → pipeline uses default templates
- Integration test: send request with invalid custom prompt → 400 error returned
- Regression test: ensure existing pipeline behavior unchanged when no custom prompts provided

**Estimated Effort:** 8 story points

---

### Story 11.6.3: Database Prompt Traceability (MVP Phase 3)

**Description:** Add `customPromptFiles` JSONB field to Experiment table, save prompt metadata with each experiment, and display prompt usage indicators in Gradio UI history.

**Acceptance Criteria:**
- Add `customPromptFiles` JSONB column to Experiment table (Prisma migration)
- When saving experiment to database via `POST /experiments/save`:
  - If custom prompts were used → populate `customPromptFiles` with metadata:
    ```json
    {
      "stage_4": {
        "filename": "stage_4_lactalis_bold_v1.2.md",
        "uploaded_at": "2025-11-24T10:30:00Z",
        "file_hash": "abc123...",  // SHA256 of content
        "file_size": 2048,
        "file_content": "Full prompt template content..."
      }
    }
    ```
  - If no custom prompts → `customPromptFiles` is null or empty JSON
- In "Experiment History" view (Story 11.1 existing feature):
  - Display 📝 icon next to experiments that used custom prompts
  - Tooltip on hover: "Custom prompts: Stage 4 (stage_4_lactalis_bold_v1.2.md)"
- When viewing experiment details:
  - New "Prompts Used" section below stage outputs
  - List stages with custom prompts: "Stage 4: stage_4_lactalis_bold_v1.2.md"
  - "📋 Download Custom Prompts" button → downloads `.md` file(s) used for that experiment
- Backend endpoint `GET /experiments/{id}/prompts` returns stored prompt files as downloadable `.md`

**Technical Notes:**
- Use `hashlib.sha256()` to generate file hash for deduplication
- Store full `file_content` in JSONB for reproducibility (not just hash reference)
- Database stores custom prompts even if experiment tagged "Failed" (for debugging)
- Download endpoint serves stored content with proper `Content-Type: text/markdown` and filename

**Test Coverage:**
- Unit test: experiment saved with custom prompts → `customPromptFiles` field populated
- Unit test: experiment saved without custom prompts → `customPromptFiles` is null
- Integration test: save experiment with custom prompts → retrieve → download prompts → content matches original upload
- UI test: experiment with custom prompts displays 📝 icon and correct tooltip
- Edge case: multiple experiments use same custom prompt (same hash) → database stores content only once per hash (optional optimization)

**Estimated Effort:** 5 story points

---

## Compatibility Requirements

- [x] Existing `/run/local` API remains unchanged when `custom_prompts` field omitted (backward compatible)
- [x] Database schema change is additive (new JSONB column, existing columns unchanged)
- [x] UI changes follow existing Gradio patterns (tabs, file upload, validation feedback)
- [x] Performance impact minimal (file upload < 1MB, validation < 1 second)
- [x] Default prompt behavior unchanged (hardcoded templates still used when no custom prompts uploaded)

## Risk Mitigation

**Primary Risk:** User uploads invalid prompt file (missing placeholders), pipeline fails with unclear error.

**Mitigation:**
- Client-side validation blocks pipeline execution if placeholders missing
- Server-side validation provides clear 400 error message if validation bypassed
- README.md in ZIP download explicitly documents required placeholders
- Error messages show exact missing placeholders (e.g., "Stage 4 missing: {insights}, {brand_context}")

**Rollback Plan:**
- Feature is fully additive (no existing code removed)
- If feature causes issues → disable "Custom Prompts" tab in Gradio UI (hide tab)
- Backend ignores `custom_prompts` field if validation logic disabled (falls back to default templates)
- Database migration adds column only (no data deletion) → safe to rollback code without DB rollback

## Definition of Done

- [x] All 3 stories completed with acceptance criteria met
- [x] Existing functionality verified through regression testing
  - Pipeline execution with NO custom prompts works identically to before
  - Database saves experiments without breaking changes
  - Gradio UI navigation and existing tabs unaffected
- [x] Integration points working correctly
  - Gradio UI → FastAPI endpoint with `custom_prompts` field
  - Backend → Dynamic prompt loading (custom vs. default)
  - Database → Prompt metadata storage and retrieval
- [x] Documentation updated appropriately
  - README.md in ZIP download for end users
  - Developer docs for API changes (`/run/local` endpoint, stage `execute()` signature)
- [x] No regression in existing features
  - All existing tests pass (Gradio UI, backend pipeline, database)
  - 95%+ test coverage maintained
  - Railway deployment successful

---

## Story Manager Handoff

**Story Manager Handoff:**

"Please develop detailed user stories for this brownfield epic. Key considerations:

- This is an enhancement to an existing Gradio experimentation system running Python 3.11 + FastAPI + PostgreSQL
- Integration points:
  - Gradio UI (`gradio_lab.py`) → FastAPI `/run/local` endpoint (httpx AsyncClient)
  - Backend pipeline stages → Prompt template files (currently hardcoded `.md`, future: dynamic)
  - Database Experiment table → New `customPromptFiles` JSONB field (additive schema change)
- Existing patterns to follow:
  - Gradio file upload pattern: `gr.File()` with validation feedback (similar to PDF upload in Story 11.1)
  - Backend validation pattern: Return 400 error with clear message on invalid input
  - Database storage pattern: Use JSONB for flexible metadata storage (similar to `stageOutputs` field)
- Critical compatibility requirements:
  - Zero breaking changes to existing default prompt behavior (backward compatible)
  - Validation must block pipeline execution on client AND server side (defense in depth)
  - Custom prompt content must be stored in database for reproducibility (full traceability)
- Each story must include verification that existing functionality remains intact:
  - Pipeline execution without custom prompts uses default templates (regression test)
  - Database schema migration is additive only (safe rollback)
  - Gradio UI tabs and navigation unaffected by new "Custom Prompts" tab

The epic should maintain system integrity while delivering the ability for non-technical users to customize LLM prompts via file upload."

---

## Validation Checklist

**Scope Validation:**
- [x] Epic can be completed in 3 stories (consolidated from original 6)
- [x] No architectural documentation required (follows existing Gradio + FastAPI patterns)
- [x] Enhancement follows existing patterns (file upload, validation, database storage)
- [x] Integration complexity is manageable (3 clear integration points)

**Risk Assessment:**
- [x] Risk to existing system is low (feature is fully additive, no code removal)
- [x] Rollback plan is feasible (disable tab, backend ignores custom_prompts field)
- [x] Testing approach covers existing functionality (regression tests for default behavior)
- [x] Team has sufficient knowledge of integration points (Gradio UI, FastAPI, PostgreSQL)

**Completeness Check:**
- [x] Epic goal is clear and achievable (enable non-technical prompt customization via file upload)
- [x] Stories are properly scoped (5 + 8 + 5 = 18 total story points)
- [x] Success criteria are measurable (50% download rate, 20% usage rate, <5% validation failures)
- [x] Dependencies are identified (Story 11.6.2 depends on 11.6.1 validation logic, 11.6.3 depends on 11.6.2 backend changes)

---

## Notes

**Original Proposal:** 6 stories (27 story points) from developer handoff document at `docs/handoff-prompts/custom-prompt-upload-feature.md`

**Consolidation Strategy (MVP Focus):**
- Story 11.6.1 combines: Download (original 11.6.1) + Upload (original 11.6.2) + Validation (original 11.6.3)
  - Rationale: These are tightly coupled UI features in same "Custom Prompts" tab
- Story 11.6.2 remains: Backend integration (original 11.6.4)
- Story 11.6.3 remains: Database traceability (original 11.6.5)
- Story 11.6.6 (Testing/Docs) distributed into DoD of Stories 1-3
  - Unit tests required for Story 1 (validation) and Story 2 (backend)
  - README.md creation part of Story 1 (included in ZIP download)

**Post-MVP Enhancements** (deferred, NOT in this epic):
- Prompt Library tab showing previously used custom prompts
- "Load from previous experiment" button to reuse prompts
- Diff view showing changes from default template
- Export experiment with prompts as self-contained ZIP
- In-browser Markdown editor (instead of upload)
- AI-assisted prompt optimization suggestions

**Total Epic Effort:** 18 story points (5 + 8 + 5)

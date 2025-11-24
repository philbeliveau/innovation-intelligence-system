# Product Handoff: Custom Prompt Upload Feature for HF Space Gradio Pipeline

**Date:** 2025-11-24
**From:** James (Dev Agent)
**To:** Product Manager
**Epic:** Enable non-technical users to customize LLM prompts via file upload
**Target Release:** Story 11.6 (Post-Railway Deployment)

---

## 🎯 Product Vision

Enable innovation teams (specifically founders at Lactalis, McCormick, Decathlon) to **customize the 7-stage pipeline prompts** without writing code. Users should be able to:

1. Download default prompt templates as `.md` files
2. Edit them locally in their preferred text editor (VS Code, Cursor, etc.)
3. Upload customized prompts to HF Space Gradio UI
4. Run the pipeline with their custom prompts
5. Track which prompt versions produced which results (traceability)

**Core Use Case:**
> "My founder wants to make Stage 4 generate BOLDER concepts. Instead of editing code, they download `stage_4_concept_generation.md`, add instructions like 'Think like a startup entering this category', save as `stage_4_lactalis_bold_v1.2.md`, upload it to Gradio, and run the pipeline."

---

## 🧑‍💼 User Personas

### **Primary User: Founder/Innovation Lead**
- **Tech Comfort:** Can use Google Docs, Slack, VS Code
- **NOT Comfortable:** Editing Python code, debugging, Git
- **Goals:**
  - Test different prompt strategies (conservative vs. bold)
  - Optimize prompts for their specific brand/industry
  - Share successful prompt versions with team
- **Pain Points:**
  - Current prompts are hardcoded in backend `.md` files
  - Changing prompts requires developer intervention
  - No way to A/B test prompt variations

### **Secondary User: Innovation Team Member**
- Receives prompt files from founder via Slack/email
- Uploads them to HF Space to reproduce experiments
- Needs validation feedback if prompt file is malformed

---

## 🏗️ System Architecture Context

### **Current Implementation (Read-Only Prompts)**

```
Pipeline Execution Flow:
1. User uploads PDF + selects brand → Gradio UI
2. Gradio calls Railway backend: POST /run/local
3. Backend executes 7 stages (Stage 0-6)
4. Each stage loads prompt from hardcoded .md file:
   backend/experimentation/prompts/stage_4_concept_generation.md
5. Prompt is formatted with data: {insights}, {brand_context}, etc.
6. Formatted prompt sent to Claude via OpenRouter API
7. Results returned to Gradio UI
```

**Limitation:** Prompts are **read-only** from backend files. Users cannot customize without code changes.

---

### **Proposed Implementation (File Upload)**

```
New Flow:
1. User clicks "Download Default Templates" → Gets ZIP with 7 .md files
2. User edits stage_4_concept_generation.md locally
3. User uploads edited file via gr.File() component in new "Custom Prompts" tab
4. Gradio validates file contains required placeholders ({insights}, {brand_context}, etc.)
5. On "Run Pipeline", Gradio sends uploaded file content to backend
6. Backend uses uploaded prompt INSTEAD of default .md file
7. Pipeline executes with custom prompt
8. Results saved with prompt file metadata (filename, hash, content)
```

---

## 📋 Required Placeholder Variables (Technical Constraint)

Each `.md` template file **MUST contain specific placeholders** that get replaced with pipeline data. Users can edit everything EXCEPT these placeholders.

| Stage | Template Filename | Required Placeholders |
|-------|------------------|----------------------|
| **Stage 0** | `stage_0_enrichment.md` | `{brand_name}`, `{industry}`, `{country}`, `{product_portfolio}` |
| **Stage 1** | `stage_1_extraction.md` | `{report_text}`, `{few_shot_examples}` |
| **Stage 2** | `stage_2_convergence.md` | `{trends}`, `{brand_context}`, `{few_shot_examples}` |
| **Stage 3** | `stage_3_technique_matching.md` | `{insights}`, `{brand_context}`, `{few_shot_examples}` |
| **Stage 4** | `stage_4_concept_generation.md` | `{insights}`, `{matched_techniques}`, `{brand_context}`, `{no_hallucination_rules}` |
| **Stage 5** | `stage_5_competitive_search.md` | `{concepts}`, `{brand_context}` |
| **Stage 6** | `stage_6_packaging.md` | `{brand_context}`, `{concepts}`, `{competitive_analysis}`, `{source_report_name}` |

**Validation Rule:** If user uploads a file missing required placeholders, show error message and prevent pipeline execution.

---

## 📦 Feature Requirements

### **Feature 1: Download Default Templates**

**As a founder, I want to download default prompt templates so I can use them as starting points for customization.**

**Acceptance Criteria:**
- [ ] New tab in Gradio UI: "📂 Custom Prompts"
- [ ] Section: "📥 Download Default Templates"
- [ ] Individual download buttons for each stage (7 buttons)
- [ ] "Download ALL (ZIP)" button that packages all 7 templates
- [ ] ZIP includes `README.md` explaining:
  - What each stage does
  - Which placeholders MUST NOT be changed
  - Example of a valid customization
- [ ] Downloaded files are named: `stage_0_enrichment.md`, `stage_1_extraction.md`, etc.
- [ ] Files are valid UTF-8 encoded Markdown

**Edge Cases:**
- What if backend template files are missing? → Show error message
- What if ZIP creation fails? → Fall back to individual file downloads

---

### **Feature 2: Upload Custom Prompts**

**As a founder, I want to upload edited prompt files so the pipeline uses my custom instructions.**

**Acceptance Criteria:**
- [ ] Section: "📤 Upload Custom Prompts"
- [ ] 7 file upload components (one per stage)
- [ ] File uploader accepts only `.md` files
- [ ] Uploaders labeled: "Stage 0 Custom Prompt (optional)"
- [ ] Help text: "Leave blank to use default prompt"
- [ ] "✅ Validate Uploaded Prompts" button
- [ ] Validation output shows per-stage status:
  - ✅ "Stage 4: Valid (all placeholders found)"
  - ❌ "Stage 4: MISSING placeholders: {insights}, {brand_context}"
  - ℹ️ "Stage 0: Using default prompt (no file uploaded)"
- [ ] Validation runs client-side (Gradio function, not backend call)
- [ ] Invalid files are highlighted in red

**Edge Cases:**
- User uploads a `.txt` file renamed to `.md` → Accept if content is valid
- User uploads file with extra placeholders (e.g., `{custom_field}`) → Allow (will be ignored)
- User uploads file with syntax errors (malformed Markdown) → Accept but warn
- User uploads 50MB file → Reject with "File too large (max 1MB)"

---

### **Feature 3: Run Pipeline with Custom Prompts**

**As a founder, I want the pipeline to use my uploaded prompts when I click "Run Pipeline".**

**Acceptance Criteria:**
- [ ] When user uploads custom prompt files and clicks "Run Pipeline":
  - Gradio reads uploaded file content
  - Sends file content to backend in `custom_prompts` field
  - Backend uses uploaded content instead of default template
- [ ] Progress indicator shows "Using custom prompts: Stage 4"
- [ ] If validation failed but user clicks "Run Pipeline" anyway → Show blocking error
- [ ] If no custom prompts uploaded → Pipeline uses defaults (existing behavior)
- [ ] Custom prompts are single-use (not persisted across sessions)

**Edge Cases:**
- User uploads Stage 4 custom prompt, runs pipeline, then removes uploaded file → Next run uses default
- User uploads custom prompts, navigates to different tab, comes back → Files still uploaded (use `gr.State()`)
- User uploads custom prompts, closes browser, reopens → Files lost (expected behavior)

---

### **Feature 4: Prompt Traceability**

**As a founder, I want to know which prompt versions produced which results so I can reproduce successful experiments.**

**Acceptance Criteria:**
- [ ] When experiment is saved to database, include:
  - `customPromptFiles`: JSON object with file metadata
  - For each uploaded stage: `filename`, `uploaded_at`, `file_hash` (SHA256), `file_size`
  - Full `file_content` (for reproducibility)
- [ ] In "Experiment History" view, show indicator if custom prompts were used:
  - Icon: 📝 "Custom prompts"
  - Tooltip: "Stage 4: stage_4_lactalis_bold_v1.2.md"
- [ ] When viewing experiment details, show:
  - "Prompts Used" section
  - List of stages with custom prompts
  - "📋 Download Custom Prompts" button (re-downloads the exact files used)
- [ ] Database stores prompt content in `customPromptFiles` JSONB field

**Edge Cases:**
- User uploads same file twice (same hash) → Database doesn't duplicate content, just references hash
- User wants to download prompts from old experiment → Backend serves stored content as `.md` file

---

### **Feature 5: Validation & Error Handling**

**As a founder, I want clear error messages if my custom prompt file is invalid.**

**Validation Rules:**

| Error Type | User-Facing Message | Blocking? |
|------------|-------------------|-----------|
| **Missing Placeholder** | "❌ Stage 4: Missing required placeholders: `{insights}`, `{brand_context}`. These are needed for pipeline data injection." | ✅ Yes - Prevent run |
| **File Too Large** | "❌ File size exceeds 1MB limit. Please reduce template size." | ✅ Yes - Prevent upload |
| **Invalid UTF-8** | "⚠️ File encoding issue detected. Please save as UTF-8." | ⚠️ Warn but allow |
| **No Markdown Headers** | "ℹ️ File has no Markdown headers. This is unusual but allowed." | ℹ️ Info only |
| **Extra Placeholders** | "ℹ️ Found unknown placeholders: `{custom_field}`. These will be ignored." | ℹ️ Info only |

**Acceptance Criteria:**
- [ ] Validation runs when user clicks "✅ Validate Uploaded Prompts"
- [ ] Validation re-runs automatically when new file is uploaded
- [ ] Blocking errors prevent "Run Pipeline" button from working (disabled state)
- [ ] Non-blocking warnings allow pipeline to run
- [ ] Validation results persist until user uploads different file

---

## 🎨 UI/UX Mockup

### **Gradio Tab Structure**

```
┌─────────────────────────────────────────────────────────────┐
│  🚀 Pipeline Runner  │  📂 Custom Prompts  │  📊 History   │
├─────────────────────────────────────────────────────────────┤
│  📂 CUSTOM PROMPTS TAB                                      │
├─────────────────────────────────────────────────────────────┤
│  ## Upload Custom Prompt Templates                          │
│                                                              │
│  Download default templates below, edit them locally,       │
│  then upload your custom versions.                          │
│  ⚠️ IMPORTANT: Keep all {placeholder} variables unchanged!  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📥 Download Default Templates                        │  │
│  │                                                       │  │
│  │  [Stage 0: Brand Enrichment]  [Stage 1: Extraction] │  │
│  │  [Stage 2: Insights]  [Stage 3: Techniques]         │  │
│  │  [Stage 4: Concepts]  [Stage 5: Competitive]        │  │
│  │  [Stage 6: Summary]   [📦 Download ALL (ZIP)]       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ 📤 Upload Custom Prompts                             │  │
│  │                                                       │  │
│  │  Stage 0 Custom Prompt (optional)                    │  │
│  │  [Drop .md file or click to browse]                 │  │
│  │                                                       │  │
│  │  Stage 1 Custom Prompt (optional)                    │  │
│  │  [Drop .md file or click to browse]                 │  │
│  │                                                       │  │
│  │  Stage 2 Custom Prompt (optional)                    │  │
│  │  [Drop .md file or click to browse]                 │  │
│  │                                                       │  │
│  │  ... (Stages 3-6 similar)                            │  │
│  │                                                       │  │
│  │  [✅ Validate Uploaded Prompts]                      │  │
│  │                                                       │  │
│  │  Validation Results:                                 │  │
│  │  ✅ Stage 0: Using default prompt                    │  │
│  │  ✅ Stage 1: Using default prompt                    │  │
│  │  ✅ Stage 2: Using default prompt                    │  │
│  │  ✅ Stage 3: Using default prompt                    │  │
│  │  ✅ Stage 4: Valid (stage_4_bold_v1.2.md)           │  │
│  │  ✅ Stage 5: Using default prompt                    │  │
│  │  ✅ Stage 6: Using default prompt                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Success Metrics

**User Adoption:**
- [ ] 50% of founders download default templates within first week
- [ ] 20% of pipeline runs use at least 1 custom prompt within first month
- [ ] Average 2-3 custom prompt versions per founder (indicates iteration)

**Quality Indicators:**
- [ ] <5% of custom prompt uploads fail validation (indicates good UX/docs)
- [ ] 80% of "Good" tagged experiments use custom prompts (indicates feature value)
- [ ] Zero support tickets about "how do I customize prompts" (indicates clear UX)

**Performance:**
- [ ] File upload validation completes <1 second (client-side)
- [ ] ZIP download generates <3 seconds
- [ ] Pipeline execution time unchanged (custom prompts don't add overhead)

---

## 🚧 Technical Constraints & Dependencies

### **Backend Changes Required**

| File | Change | Effort |
|------|--------|--------|
| `pipeline_orchestrator.py` | Add `custom_prompts` parameter to `run_pipeline()` | 1 hour |
| `stages/stage_0-6.py` | Add `custom_prompt_content` parameter to `execute()` | 3 hours (7 files) |
| `prompt_file_validator.py` | Create new validator class | 2 hours |
| `app/api/pipeline.py` | Accept `custom_prompts` in `/run/local` endpoint | 30 min |
| `prisma/schema.prisma` | Add `customPromptFiles` JSONB field | 30 min + migration |

**Total Backend Effort:** 7-8 hours

### **Frontend Changes Required**

| Component | Change | Effort |
|-----------|--------|--------|
| `hf-space-deploy/app.py` | Add "Custom Prompts" tab with download buttons | 2 hours |
| `hf-space-deploy/app.py` | Add 7 file upload components + validation UI | 3 hours |
| `hf-space-deploy/app.py` | Integrate file upload with pipeline execution | 2 hours |
| Helper functions | Create ZIP generator, file reader, validator | 2 hours |

**Total Frontend Effort:** 9 hours

### **Testing & Documentation**

- Unit tests for `PromptFileValidator` (2 hours)
- Integration tests for file upload → pipeline flow (3 hours)
- User documentation (`README.md` in ZIP) (1 hour)
- Developer documentation (API changes) (1 hour)

**Total Testing/Docs Effort:** 7 hours

---

## 🔐 Security & Privacy Considerations

### **File Upload Security**

**Threats:**
- Malicious `.md` files with code injection attempts
- Large files causing memory issues
- XSS via Markdown rendering

**Mitigations:**
- [ ] Limit file size to 1MB (prevents DoS)
- [ ] Validate UTF-8 encoding (prevents binary exploits)
- [ ] Sanitize Markdown before rendering in Gradio (prevent XSS)
- [ ] Do NOT execute any code from uploaded files (treat as pure text)
- [ ] Store uploaded content in database as text, not as executable files

### **Data Privacy**

**Concern:** Custom prompts may contain brand-specific information (product names, strategies)

**Mitigations:**
- [ ] Store prompts in same PostgreSQL database as experiments (already encrypted at rest)
- [ ] Do NOT log prompt content to stdout/stderr (only log metadata)
- [ ] Do NOT share prompts across different brand accounts (if multi-tenancy added later)

---

## 🎓 User Education & Onboarding

### **In-App Guidance**

**README.md** (included in ZIP download):

```markdown
# Innovation Pipeline Custom Prompts

## What are these files?

These are **prompt templates** that control how our AI generates insights and concepts. Think of them as "instruction manuals" for Claude (the AI).

## How to use them:

1. **Download** this ZIP and extract the `.md` files
2. **Open** a file (e.g., `stage_4_concept_generation.md`) in any text editor
3. **Edit** the instructions, but **DO NOT change anything in curly braces** like `{insights}` or `{brand_context}` - these are data injection points
4. **Save** your edited file with a version name (e.g., `stage_4_bold_v1.2.md`)
5. **Upload** it back to the HF Space "Custom Prompts" tab
6. **Run** your pipeline - it will now use your custom instructions!

## Example Customization:

**Original (Stage 4):**
> Generate 3-5 directional concepts...

**Your Version:**
> Generate 3-5 **BOLD, CATEGORY-CHALLENGING** concepts that startups would create. Think disruptive, not incremental.

## Required Placeholders (DON'T REMOVE):

- Stage 0: `{brand_name}`, `{industry}`, `{country}`, `{product_portfolio}`
- Stage 1: `{report_text}`, `{few_shot_examples}`
- Stage 2: `{trends}`, `{brand_context}`, `{few_shot_examples}`
- Stage 3: `{insights}`, `{brand_context}`, `{few_shot_examples}`
- Stage 4: `{insights}`, `{matched_techniques}`, `{brand_context}`, `{no_hallucination_rules}`
- Stage 5: `{concepts}`, `{brand_context}`
- Stage 6: `{brand_context}`, `{concepts}`, `{competitive_analysis}`, `{source_report_name}`

## Questions?

Contact: [support email]
```

---

## 📅 Suggested User Stories Breakdown

### **Epic: Custom Prompt Upload System**

**Story 11.6.1: Download Default Templates** (3 points)
- As a founder, I want to download default prompt templates as `.md` files so I can edit them locally
- Includes: Download buttons UI, ZIP generator, README.md creation

**Story 11.6.2: Upload Custom Prompt Files** (5 points)
- As a founder, I want to upload edited prompt files so the pipeline uses my custom instructions
- Includes: File upload UI (7 components), gr.File() integration, session state management

**Story 11.6.3: Client-Side Prompt Validation** (3 points)
- As a founder, I want validation feedback on uploaded prompts so I know if they're valid before running the pipeline
- Includes: Placeholder checker, validation UI, error messages

**Story 11.6.4: Backend Custom Prompt Integration** (8 points)
- As a developer, I want the backend to accept and use custom prompt content instead of default templates
- Includes: `PromptFileValidator` class, modify 7 stage files, update orchestrator, update API endpoint

**Story 11.6.5: Prompt Traceability in Database** (5 points)
- As a founder, I want to see which prompt versions produced which results so I can reproduce successful experiments
- Includes: Database schema change, save prompt metadata, display in UI, download feature

**Story 11.6.6: Testing & Documentation** (3 points)
- As a developer, I want comprehensive tests and docs so the feature is reliable and maintainable
- Includes: Unit tests, integration tests, user docs, developer docs

**Total Epic Effort:** 27 story points (~5-6 sprints at 5 points/sprint)

---

## 🎯 Acceptance Criteria for Epic Completion

### **Must Have (MVP)**
- [x] User can download all 7 default templates as individual files or ZIP
- [x] User can upload custom `.md` files for any stage (optional, 0-7 files)
- [x] Validation shows which stages use custom vs. default prompts
- [x] Validation blocks pipeline if required placeholders are missing
- [x] Pipeline executes with custom prompts when uploaded
- [x] Experiment database stores which prompt files were used (metadata + content)
- [x] Zero breaking changes to existing default prompt behavior

### **Should Have (Post-MVP)**
- [ ] "Prompt Library" tab showing previously used custom prompts
- [ ] "Load from previous experiment" button to reuse prompts
- [ ] Diff view showing changes from default template
- [ ] Export experiment with prompts as self-contained ZIP

### **Nice to Have (Future)**
- [ ] In-browser Markdown editor (instead of upload)
- [ ] Syntax highlighting for placeholders in uploaded files
- [ ] AI-assisted prompt optimization suggestions
- [ ] Team prompt library with sharing/approval workflow

---

## ⚠️ Known Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| **User accidentally removes required placeholder** | High - Pipeline fails | High | Validation blocks execution + clear error message |
| **User uploads 50MB file** | Medium - Memory issue | Low | Hard limit at 1MB |
| **User expects code execution in prompts** | Low - Confusion | Low | Documentation clarifies "instructions, not code" |
| **Database storage bloat from prompt content** | Medium - Cost increase | Medium | Deduplicate by hash, compress text |
| **User loses custom prompts when browser refreshes** | Low - Frustration | Medium | Clear messaging "Files not persisted across sessions" |

---

## 📞 Questions for PM to Resolve

1. **File Size Limit:** Is 1MB sufficient for prompt templates? (Current templates are 2-5KB)
2. **Session Persistence:** Should uploaded files persist across browser refreshes? (Requires server-side storage)
3. **Multi-User Collaboration:** Should teams share a "prompt library" or is file-based sharing via Slack sufficient?
4. **Version Naming:** Should we enforce a naming convention (e.g., `stage_4_v1.2_lactalis.md`) or allow freeform?
5. **Rollback:** If user's custom prompt produces bad results, should there be a "Revert to Default" button?
6. **Analytics:** Do we need telemetry to track which prompt modifications correlate with "Good" quality tags?

---

## 🚀 Suggested Rollout Plan

### **Phase 1: Internal Alpha** (Week 1-2)
- Deploy to HF Space with feature flag
- Test with 2-3 internal users (founders at Lactalis/McCormick)
- Gather feedback on UX, validation messages, error handling

### **Phase 2: Beta Release** (Week 3-4)
- Enable for all HF Space users
- Monitor error rates, validation failures, support tickets
- Iterate on documentation based on user questions

### **Phase 3: GA Release** (Week 5)
- Announce feature in user onboarding email
- Create video tutorial showing download → edit → upload flow
- Measure adoption metrics (downloads, uploads, success rate)

### **Phase 4: Iteration** (Week 6+)
- Build "Should Have" features based on usage data
- Optimize validation performance if needed
- Add prompt library if users request sharing capabilities

---

## 📚 Reference Materials

**Existing Documentation:**
- HF Space deployment guide: `/backend/experimentation/hf-space-deploy/DEPLOYMENT.md`
- Default prompt templates: `/backend/experimentation/prompts/*.md`
- Pipeline architecture: `/docs/architecture/project-structure.md`
- Gradio file upload docs: https://www.gradio.app/docs/gradio/file

**Related Stories:**
- Story 11.1: Gradio UI implementation (completed)
- Story 11.4: Database persistence (completed)
- Story 11.5: Railway deployment (in progress)

---

## ✅ PM Action Items

1. Review this handoff document for completeness
2. Break down Epic into user stories with acceptance criteria
3. Prioritize stories in backlog (recommend 11.6.1 → 11.6.2 → 11.6.3 → 11.6.4 → 11.6.5)
4. Answer outstanding questions (Section: "Questions for PM to Resolve")
5. Schedule design review for "Custom Prompts" tab UI mockup
6. Identify beta test users for Phase 1 rollout
7. Create Jira/Linear tickets with story points
8. Schedule kickoff meeting with dev team

---

**END OF HANDOFF**

---

**Next Steps:**
PM to acknowledge receipt and confirm story breakdown approach. Dev team ready to begin implementation once stories are refined and prioritized.

# Story Template Format - BMAD Core

All user stories in this directory follow the **BMAD™ Core story template** (v2.0) as defined in:
`.bmad-core/templates/story-tmpl.yaml`

---

## Story Naming Convention

**Format:** `{epic_num}.{story_num}.{story-title-short}.md`

**Examples:**
- `1.1.landing-page-company-selection.md`
- `1.2.file-upload-vercel-blob.md`
- `1.3.upload-page-ui-company-badge.md`

---

## Required Template Sections

### 1. **Status**
- Type: Choice
- Options: Draft | Approved | InProgress | Review | Done
- Owner: Scrum Master
- Editors: Scrum Master, Dev Agent

### 2. **Story**
- Type: Template Text
- Format:
  ```
  **As a** {role},
  **I want** {action},
  **so that** {benefit}
  ```
- Owner: Scrum Master
- Elicit: Yes

### 3. **Acceptance Criteria**
- Type: Numbered List
- Copied from epic file
- Owner: Scrum Master
- Elicit: Yes

### 4. **Tasks / Subtasks**
- Type: Bullet List with checkboxes
- Format:
  ```
  - [ ] Task 1 (AC: #1, #2, #3)
    - [ ] Subtask 1.1
    - [ ] Subtask 1.2
  - [ ] Task 2 (AC: #4)
    - [ ] Subtask 2.1
  ```
- References applicable AC numbers
- Owner: Scrum Master, Dev Agent
- Elicit: Yes

### 5. **Dev Notes**
- Type: Free Text
- Content:
  - Relevant source tree info
  - Important notes from previous stories
  - Complete context for dev agent (no need to read architecture docs)
- Owner: Scrum Master
- Elicit: Yes

#### 5.1. **Testing** (Subsection)
- Test file location
- Test standards
- Testing frameworks and patterns
- Specific testing requirements for story
- Owner: Scrum Master
- Elicit: Yes

### 6. **Change Log**
- Type: Table
- Columns: Date | Version | Description | Author
- Owner: Scrum Master
- Editors: Scrum Master, Dev Agent, QA Agent

### 7. **Dev Agent Record**
- Type: Section (populated by dev agent)
- Owner: Dev Agent

#### 7.1. **Agent Model Used**
- Record AI agent model and version
- Owner: Dev Agent

#### 7.2. **Debug Log References**
- Links to debug logs/traces
- Owner: Dev Agent

#### 7.3. **Completion Notes List**
- Notes about task completion and issues
- Owner: Dev Agent

#### 7.4. **File List**
- All files created, modified, or affected
- Owner: Dev Agent

### 8. **QA Results**
- Type: Free Text
- Results from QA agent review
- Owner: QA Agent

---

## Template Workflow

- **Mode:** Interactive
- **Elicitation:** Advanced elicitation enabled for key sections
- **Editable Sections:** Status, Story, Acceptance Criteria, Tasks/Subtasks, Dev Notes, Testing, Change Log

---

## Story Lifecycle

1. **Draft** - Story created by PM, under review
2. **Approved** - Ready for implementation
3. **InProgress** - Dev agent actively working on story
4. **Review** - Implementation complete, awaiting QA review
5. **Done** - QA passed, story fully completed

---

## Agent Responsibilities

| Agent | Responsibilities |
|-------|------------------|
| **Scrum Master (PM)** | Create story, define AC, create tasks, provide dev notes, approve story |
| **Dev Agent** | Update task status, populate dev agent record, complete implementation |
| **QA Agent** | Populate QA results, verify AC met, approve completion |

---

## Key Principles

1. **Complete Context:** Dev notes must contain all info needed - dev agent should NOT need to read architecture docs
2. **AC References:** Tasks/subtasks must reference applicable AC numbers
3. **No Invention:** Dev notes should only contain info from actual project artifacts
4. **Testing Standards:** Testing section must specify exact frameworks, patterns, and requirements
5. **Traceability:** Change log tracks all modifications with author attribution

---

## Example Story Structure

```markdown
# Story 1.1: Feature Name

**Epic:** Epic 1 - Epic Name
**Priority:** P0
**Estimated Time:** X hours

---

## Status

**Draft**

---

## Story

**As a** user role,
**I want** specific action,
**so that** clear benefit.

---

## Acceptance Criteria

1. First acceptance criterion
2. Second acceptance criterion
3. Third acceptance criterion

---

## Tasks / Subtasks

- [ ] Task 1: Description (AC: #1, #2)
  - [ ] Subtask 1.1
  - [ ] Subtask 1.2
- [ ] Task 2: Description (AC: #3)
  - [ ] Subtask 2.1

---

## Dev Notes

### Integration Points
- Point 1
- Point 2

### Technical Details
- Detail 1
- Detail 2

### Testing

#### Test Standards
- Standard 1
- Standard 2

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-19 | 1.0 | Initial creation | PM Agent |

---

## Dev Agent Record

### Agent Model Used
*To be populated by dev agent*

### Debug Log References
*To be populated by dev agent*

### Completion Notes List
*To be populated by dev agent*

### File List
*To be populated by dev agent*

---

## QA Results

*To be populated by QA agent*
```

---

## BMAD Template Benefits

✅ **Standardization** - Consistent format across all stories
✅ **Traceability** - Change log and agent records track history
✅ **Completeness** - All necessary info captured upfront
✅ **Agent-Ready** - Dev notes eliminate need for architecture doc reads
✅ **Testability** - Testing standards specified per story
✅ **Accountability** - Clear ownership and editor permissions

---

**Template Version:** 2.0
**Template File:** `.bmad-core/templates/story-tmpl.yaml`
**Last Updated:** 2025-10-19

# Story 3.1: Pre-Existing Research Data Integration

## Status
Approved

## Story
**As a** pipeline developer,
**I want** to load and access pre-existing research data from local files,
**so that** Stage 4 can use completed brand research without live web searches.

## Acceptance Criteria
1. Research data loader created in `pipeline/utils.py`: `load_research_data(brand_id)` function that reads from `docs/web-search-setup/{brand-id}-research.md`
2. Function loads single comprehensive markdown file per brand containing 8 strategic sections (~550-720 lines, 35-48KB):
   - Brand Overview & Positioning
   - Product Portfolio & Innovation
   - Recent Innovations (Last 18 Months)
   - Strategic Priorities & Business Strategy
   - Target Customers & Market Positioning
   - Sustainability & Social Responsibility
   - Competitive Context & Market Trends
   - Recent News & Market Signals (Last 6 Months)
3. Function returns complete research content as string for injection into Stage 4 prompt
4. Test script created: `test_research_loader.py` that:
   - Lists all 4 available research files (lactalis-canada, mccormick-usa, columbia-sportswear, decathlon)
   - Loads each research file and verifies successful parsing (UTF-8 encoding)
   - Validates file statistics: line count, size, confirms 8 sections present
   - Tests graceful handling of missing files
5. Error handling implemented: If research file missing or unreadable, log warning and return empty string (non-fatal)
6. Logging added: Log file path, line count, and size (KB) when research data loaded
7. Documentation: `docs/brand-research-data-structure.md` documents the 8-section format, file naming convention (`{brand-id}-research.md`), and Stage 4 integration pattern

## Tasks / Subtasks
- [ ] Create research data loader function (AC: 1, 3)
  - [ ] Add `load_research_data(brand_id)` to `pipeline/utils.py`
  - [ ] Implement file path resolution for `docs/web-search-setup/{brand-id}-research.md`
  - [ ] Read markdown file content as string
  - [ ] Return complete content for prompt injection
- [ ] Implement error handling and logging (AC: 5, 6)
  - [ ] Add try/except for file read errors
  - [ ] Log warning if file missing or unreadable
  - [ ] Return empty string on error (non-fatal)
  - [ ] Log successful load with file stats (path, line count, size)
- [ ] Create test script (AC: 4)
  - [ ] Create `test_research_loader.py`
  - [ ] List all 4 research files
  - [ ] Test loading each file with UTF-8 encoding
  - [ ] Validate file statistics (lines, size, sections)
  - [ ] Test graceful handling of missing files
- [ ] Document research data structure (AC: 2, 7)
  - [ ] Create `docs/brand-research-data-structure.md`
  - [ ] Document 8-section format
  - [ ] Document file naming convention
  - [ ] Explain Stage 4 integration pattern
  - [ ] Provide example usage

## Dev Notes

**Epic:** Epic 3 - Brand Contextualization with Research Data (Stage 4)

**Dependencies:**
- Story 1.4 (Output Directory Structure and Logging)
- Pre-existing research files in `docs/web-search-setup/`

**Technical Requirements:**
- Research files are in `docs/web-search-setup/` directory
- Files are markdown format with consistent structure
- UTF-8 encoding required
- Graceful degradation if files missing (non-fatal error)

**Key Implementation Notes:**
- Function must handle missing files gracefully
- Logging provides visibility into research data usage
- Research files average 35-48KB, 550-720 lines
- 8 strategic sections provide comprehensive brand context

**File Naming Convention:**
- Pattern: `{brand-id}-research.md`
- Examples: `lactalis-canada-research.md`, `mccormick-usa-research.md`

### Testing
**Test file location:** Root directory (`test_research_loader.py`)
**Test standards:** Verify successful file loading and error handling
**Testing frameworks:** Python file I/O, UTF-8 encoding
**Specific requirements:**
- Test all 4 brand research files
- Verify UTF-8 encoding handling
- Validate file statistics (lines, size, sections)
- Test missing file error handling
- Confirm non-fatal error behavior

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| TBD | 1.0 | Initial story creation | Unassigned |

## Dev Agent Record

### Agent Model Used
Not yet implemented

### Debug Log References
Not yet implemented

### Completion Notes List
Not yet implemented

### File List
Not yet implemented

## QA Results
Not yet completed

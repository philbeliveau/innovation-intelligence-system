# Epic: User Run Management & History - User Stories

## Story 1.1: Sidebar Run History Navigation

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to see my recent pipeline runs in the left sidebar,
**so that** I can quickly access my past analyses without navigating away from the current page.

### Acceptance Criteria

1. **Sidebar Section Added**
   - "My Runs" section appears below "Home" navigation item
   - Section displays last 5 runs (most recent first)
   - Each run shows: truncated document name (20 chars), company name, relative timestamp, status badge, card count

2. **Status Indicators**
   - PROCESSING: Blue spinner icon (🔄) with animation
   - COMPLETED: Green checkmark (✅)
   - FAILED: Red X (❌)
   - CANCELLED: Gray circle (⭕)

3. **Click Interactions**
   - Click run item → Navigate to `/runs/[runId]` (run detail page)
   - Click "View All Runs" link → Navigate to `/runs` (run history page)

4. **Real-Time Updates**
   - Sidebar polls `/api/runs?pageSize=5` every 10 seconds when user is on pipeline viewer
   - Processing runs show animated spinner
   - Newly completed runs appear at top of list

5. Existing sidebar collapse/expand behavior continues to work unchanged

6. Sidebar width accommodates run metadata (min-width: 240px)

7. Integration with Clerk maintains current auth behavior (shows only user's runs)

8. Loading state displays skeleton placeholders while fetching runs

9. Error state shows friendly message if API call fails

10. Component is fully responsive (collapses to icon-only on mobile)

### Tasks / Subtasks

- [ ] Create sidebar run history component (AC: 1, 2)
  - [ ] Add "My Runs" section to LeftSidebar.tsx
  - [ ] Implement run card display with truncated document name, company, timestamp, status, card count
  - [ ] Add status badge icons with proper styling

- [ ] Implement API integration (AC: 1, 4)
  - [ ] Create fetch hook for `/api/runs?pageSize=5`
  - [ ] Implement polling with useEffect and setInterval (10-second interval)
  - [ ] Add conditional polling (only when on pipeline viewer page)

- [ ] Add navigation handlers (AC: 3)
  - [ ] Implement onClick navigation to `/runs/[runId]`
  - [ ] Add "View All Runs" link with navigation to `/runs`

- [ ] Handle loading and error states (AC: 8, 9)
  - [ ] Create skeleton placeholders for loading state
  - [ ] Add error message UI component
  - [ ] Implement retry mechanism for failed API calls

- [ ] Ensure responsive design (AC: 5, 6, 10)
  - [ ] Test collapse/expand behavior with new section
  - [ ] Verify min-width: 240px
  - [ ] Test mobile responsive behavior (icon-only collapse)

- [ ] Write unit tests (DoD)
  - [ ] Test sidebar component rendering
  - [ ] Test polling behavior
  - [ ] Test navigation handlers
  - [ ] Test loading and error states

### Dev Notes

**Existing System Integration:**
- Integrates with: Existing `LeftSidebar.tsx` component
- Technology: Next.js 15, React Server Components, shadcn/ui
- Follows pattern: Collapsible sidebar with hover interaction (already implemented)
- Touch points: `/api/runs` API route (to be created), Clerk auth session

**API Endpoint:** `GET /api/runs?page=1&pageSize=5`

**Data Structure:**
```typescript
interface SidebarRun {
  id: string
  documentName: string
  companyName: string
  createdAt: string
  status: RunStatus
  cardCount: number
}
```

**Polling Implementation:**
- Use `useEffect` with `setInterval` for runs in PROCESSING state
- Clean up interval on component unmount

**Existing Pattern Reference:**
- See `LeftSidebar.tsx` lines 45-67 for hover interaction pattern
- Match brutalist design aesthetic of existing cards

**Component Location:**
- `innovation-web/src/components/LeftSidebar.tsx`

#### Testing

**Test File Location:** `innovation-web/src/components/__tests__/LeftSidebar.test.tsx`

**Testing Standards:**
- Use React Testing Library
- Test user interactions (click, hover)
- Mock API calls with MSW (Mock Service Worker)
- Test polling behavior with fake timers
- Verify responsive behavior with different viewport sizes

**Testing Framework:** Jest + React Testing Library

**Specific Testing Requirements:**
- Test sidebar renders "My Runs" section
- Test polling starts/stops correctly
- Test navigation on click events
- Test loading skeleton display
- Test error state rendering
- Verify existing sidebar functionality unchanged

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.2: Run History Page with Filtering

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to view all my past pipeline runs in a searchable, filterable grid,
**so that** I can find specific analyses by company, date, or status.

### Acceptance Criteria

1. **Page Layout**
   - Route: `/app/runs/page.tsx`
   - Grid layout: 3 columns on desktop (lg:grid-cols-3), 1 column on mobile
   - Header shows: "Your Innovation Runs" + total count + unique company count

2. **Run Cards Display**
   - Each card uses brutalist design: 5px solid black border, 8px shadow offset
   - Card content: Document name (truncated), company badge, relative date, status icon
   - Hover effect: Card lifts with translate(-3px, -3px) and shadow adjustment
   - Metrics row: `{cardCount} cards` · `{duration}` (if completed)

3. **Filter Controls**
   - Company multi-select dropdown (shows all companies user has used)
   - Status filter: "All", "Completed", "Processing", "Failed"
   - Date range filter: "Today", "This Week", "This Month", "All Time"
   - Search input: Filter by document name (case-insensitive)

4. **Sorting Options**
   - Sort by: "Newest First" (default), "Oldest First", "Company A-Z"
   - Sorting preference saved to localStorage

5. **Pagination**
   - 12 runs per page
   - Page controls at bottom: Previous, page numbers, Next
   - URL reflects current page: `/runs?page=2`

6. **Card Actions**
   - "View" button → Navigate to `/runs/[runId]`
   - "Rerun" button → Trigger POST `/api/runs/[runId]/rerun`, navigate to new run's pipeline viewer
   - "Delete" button → Show confirmation modal, call DELETE `/api/runs/[runId]`

7. API calls use `GET /api/runs?page={n}&pageSize=12&companyId={id}&status={status}`

8. Clerk authentication enforces user isolation (only user's runs visible)

9. Empty state shows when no runs exist: "No runs yet. Upload a document to get started."

10. Loading state shows 12 skeleton cards while fetching data

11. Filter changes trigger immediate refetch with new parameters

12. Delete action shows optimistic UI update (card removed immediately)

13. Error fetching runs shows friendly error message with retry button

### Tasks / Subtasks

- [ ] Create run history page component (AC: 1, 2)
  - [ ] Create `app/runs/page.tsx`
  - [ ] Implement grid layout with responsive columns
  - [ ] Add page header with title, total count, company count
  - [ ] Create run card component with brutalist styling
  - [ ] Add hover effects to cards

- [ ] Implement filter controls (AC: 3, 4)
  - [ ] Add company multi-select dropdown using shadcn/ui Select
  - [ ] Add status filter dropdown
  - [ ] Add date range filter dropdown
  - [ ] Add search input for document name filtering
  - [ ] Add sorting dropdown with localStorage persistence

- [ ] Implement pagination (AC: 5)
  - [ ] Add pagination controls component
  - [ ] Implement URL state management with useSearchParams
  - [ ] Handle page navigation (previous, next, specific page)

- [ ] Add card actions (AC: 6)
  - [ ] Add "View" button with navigation to detail page
  - [ ] Add "Rerun" button with confirmation modal
  - [ ] Add "Delete" button with confirmation modal
  - [ ] Implement optimistic UI for delete action

- [ ] Implement API integration (AC: 7, 8)
  - [ ] Create API fetch hook with query parameters
  - [ ] Handle Clerk authentication in API calls
  - [ ] Implement refetch on filter changes

- [ ] Handle edge cases (AC: 9, 10, 11, 12, 13)
  - [ ] Create empty state component
  - [ ] Create loading skeleton cards (12 cards)
  - [ ] Add error state with retry button
  - [ ] Implement optimistic UI for delete

- [ ] Write integration tests (DoD)
  - [ ] Test filtering logic
  - [ ] Test pagination navigation
  - [ ] Test sorting behavior
  - [ ] Test card actions (view, rerun, delete)
  - [ ] Test empty, loading, and error states

### Dev Notes

**Existing System Integration:**
- Integrates with: Existing `/app` routing structure
- Technology: Next.js 15 App Router, Prisma Client, shadcn/ui
- Follows pattern: Brutalist card grid matching `OpportunityCard` design (see PRD section 5.6)
- Touch points: `/api/runs` API route with query parameters, Clerk auth

**API Endpoint:** `GET /api/runs` (see PRD section 4.6.5 lines 1511-1565)

**Prisma Query Pattern:**
```typescript
await prisma.run.findMany({
  where: {
    userId,
    companyId: companyId || undefined,
    status: status || undefined,
    createdAt: dateRange ? { gte: startDate, lte: endDate } : undefined,
    documentName: searchQuery ? { contains: searchQuery, mode: 'insensitive' } : undefined
  },
  skip: (page - 1) * 12,
  take: 12,
  orderBy: { createdAt: 'desc' }
})
```

**shadcn/ui Components:**
- `Card` for run cards
- `Select` for company and status filters
- `Input` for search
- `Button` for pagination and actions
- `Dialog` for delete confirmation

**State Management:**
- Use `useState` for filters
- Use `useSearchParams` for pagination
- Use localStorage for sorting preference

**Existing Pattern:** Match brutalist card design from `OpportunityCard` (PRD section 5.6 lines 346-372)

**Component Location:**
- `innovation-web/src/app/runs/page.tsx`
- `innovation-web/src/components/RunCard.tsx` (new)
- `innovation-web/src/components/RunFilters.tsx` (new)

#### Testing

**Test File Location:**
- `innovation-web/src/app/runs/__tests__/page.test.tsx`
- `innovation-web/src/components/__tests__/RunCard.test.tsx`

**Testing Standards:**
- Use React Testing Library
- Test filtering logic with different combinations
- Mock Prisma database queries
- Test pagination with URL state changes
- Verify responsive grid layout

**Testing Framework:** Jest + React Testing Library + Prisma mock

**Specific Testing Requirements:**
- Test all filter combinations work correctly
- Test pagination navigation updates URL
- Test sorting persists to localStorage
- Test optimistic delete updates UI immediately
- Test empty state renders when no runs
- Test loading skeleton displays during fetch
- Test error state with retry functionality

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.3: Run Detail Page with Tabs

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to view complete details of a specific pipeline run including all opportunity cards and stage outputs,
**so that** I can review the full analysis and export cards I'm interested in.

### Acceptance Criteria

1. **Page Header**
   - Route: `/app/runs/[runId]/page.tsx`
   - Breadcrumbs: "Home > My Runs > {documentName}"
   - Metadata row: Company badge, Date (formatted), Duration (if completed), Pipeline version
   - Action buttons: "Rerun" (with same document), "Download PDF", "Delete Run"

2. **Tab Navigation**
   - Tab 1 (default): "Opportunity Cards" - Grid of 5 cards
   - Tab 2: "Full Report" - Inspiration report with 2 tracks
   - Tab 3: "Pipeline Stages" - Stage-by-stage output visualization
   - Tab state persisted in URL: `/runs/[runId]?tab=cards`

3. **Opportunity Cards Tab**
   - Display all cards in grid matching results page layout
   - Each card shows star/favorite button (top-right corner)
   - Click star → POST `/api/cards/[cardId]/star`, toggle visual state
   - Starred cards show filled star (⭐), unstarred show outline (☆)
   - Click card → Expand in modal with full markdown rendering

4. **Full Report Tab**
   - Display `InspirationReport` data from run
   - Show both ideation tracks (selected and non-selected)
   - Render stage outputs 1-5 with markdown formatting
   - Collapsible sections for each stage (use `Accordion` component)

5. **Pipeline Stages Tab**
   - Show vertical timeline of 5 stages
   - Each stage: Number, name, completion time, status badge
   - Expandable sections showing JSON output data (formatted)
   - Visual indicators: Completed stages green, failed stages red

6. API call `GET /api/runs/[runId]` fetches run with all relations (PRD lines 1569-1615)

7. Prisma query includes: `opportunityCards`, `inspirationReport`, `stageOutputs`

8. Clerk auth ensures only run owner can access (404 if unauthorized)

9. If run status is PROCESSING, show polling UI with real-time updates

10. Loading state shows skeleton UI for header and tabs

11. 404 page renders if run not found or user lacks access

12. Starred state updates optimistically (instant visual feedback)

13. PDF download generates document with all 5 opportunity cards

14. Mobile responsive: Tabs stack vertically, cards display single column

### Tasks / Subtasks

- [ ] Create run detail page layout (AC: 1, 2)
  - [ ] Create `app/runs/[runId]/page.tsx`
  - [ ] Add breadcrumbs navigation
  - [ ] Add metadata row with company badge, date, duration, version
  - [ ] Add action buttons (Rerun, Download PDF, Delete)
  - [ ] Implement tab navigation using shadcn/ui Tabs component
  - [ ] Add URL state management for active tab

- [ ] Implement Opportunity Cards tab (AC: 3)
  - [ ] Display cards in grid layout matching results page
  - [ ] Add star/favorite button to each card
  - [ ] Implement star toggle with POST `/api/cards/[cardId]/star`
  - [ ] Add optimistic UI update for starred state
  - [ ] Create card expansion modal with markdown rendering

- [ ] Implement Full Report tab (AC: 4)
  - [ ] Fetch and display InspirationReport data
  - [ ] Render both ideation tracks
  - [ ] Display stage outputs 1-5 with markdown formatting
  - [ ] Add collapsible sections using Accordion component

- [ ] Implement Pipeline Stages tab (AC: 5)
  - [ ] Create vertical timeline component
  - [ ] Display 5 stages with number, name, completion time, status
  - [ ] Add expandable sections for JSON output
  - [ ] Add visual indicators (green for completed, red for failed)

- [ ] Implement API integration (AC: 6, 7, 8, 9)
  - [ ] Create fetch hook for `GET /api/runs/[runId]`
  - [ ] Add Prisma includes for related data
  - [ ] Implement Clerk auth verification
  - [ ] Add polling for PROCESSING runs
  - [ ] Handle 404 for unauthorized access

- [ ] Implement PDF download (AC: 13)
  - [ ] Install jsPDF or react-pdf library
  - [ ] Create PDF generation function
  - [ ] Include all 5 opportunity cards in PDF
  - [ ] Add download trigger to action button

- [ ] Handle edge cases (AC: 10, 11, 12, 14)
  - [ ] Create loading skeleton UI
  - [ ] Create 404 page component
  - [ ] Implement optimistic UI for star toggle
  - [ ] Ensure mobile responsive layout

- [ ] Write tests (DoD)
  - [ ] Test tab navigation with URL state
  - [ ] Test star toggle functionality
  - [ ] Test modal expansion
  - [ ] Test PDF download generation
  - [ ] Test 404 handling
  - [ ] Test mobile responsive behavior

### Dev Notes

**Existing System Integration:**
- Integrates with: Existing results page layout and opportunity card components
- Technology: Next.js 15 dynamic routes, Prisma includes, shadcn/ui Tabs
- Follows pattern: Existing `/results` page structure with card rendering
- Touch points: `/api/runs/[runId]` API route, `/api/cards/[cardId]/star` endpoint

**API Endpoint:** `GET /api/runs/[runId]` (PRD lines 1569-1615)

**Prisma Include Pattern:**
```typescript
include: {
  opportunityCards: { orderBy: { number: 'asc' } },
  inspirationReport: true,
  stageOutputs: { orderBy: { stageNumber: 'asc' } }
}
```

**shadcn/ui Components:**
- `Tabs` for tab navigation
- `Accordion` for collapsible sections
- `Dialog` for card modal expansion
- `Button` for star toggle and actions

**PDF Generation:**
- Use `jsPDF` or `react-pdf` to generate downloadable PDF
- Include all 5 opportunity cards with full content
- Maintain brutalist styling in PDF output

**Markdown Rendering:**
- Use `react-markdown` with existing styling from results page
- Ensure security with proper sanitization

**Component Location:**
- `innovation-web/src/app/runs/[runId]/page.tsx`
- `innovation-web/src/components/RunDetailTabs.tsx` (new)
- `innovation-web/src/components/PipelineStagesTimeline.tsx` (new)

#### Testing

**Test File Location:**
- `innovation-web/src/app/runs/[runId]/__tests__/page.test.tsx`

**Testing Standards:**
- Use React Testing Library
- Mock Prisma database queries with all includes
- Test dynamic route parameters
- Test PDF generation output
- Verify markdown rendering security

**Testing Framework:** Jest + React Testing Library + Prisma mock

**Specific Testing Requirements:**
- Test all three tabs render correctly
- Test URL state updates when switching tabs
- Test star toggle updates database and UI
- Test modal expansion displays full card content
- Test PDF download generates valid document
- Test 404 handling for non-existent or unauthorized runs
- Test polling behavior for PROCESSING runs
- Test mobile responsive tab stacking

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.4: Rerun Pipeline Functionality

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to re-execute a pipeline with the same document and company parameters,
**so that** I can compare different runs or retry failed analyses without re-uploading the document.

### Acceptance Criteria

1. **Rerun Button - Run Detail Page**
   - "Rerun" button in page header (top-right)
   - Click → Show confirmation modal: "Re-run this analysis? A new run will be created with the same document and company."
   - Confirm → POST `/api/runs/[runId]/rerun`
   - Success → Navigate to `/pipeline/[newRunId]` (new run's pipeline viewer)

2. **Rerun Button - Run History Page**
   - Each run card has "Rerun" action button
   - Click → Same confirmation modal as above
   - Confirm → POST `/api/runs/[runId]/rerun`
   - Success → Navigate to `/pipeline/[newRunId]`

3. **API Behavior**
   - Endpoint: `POST /api/runs/[runId]/rerun`
   - Fetches original run's parameters: `companyId`, `companyName`, `documentName`, `documentUrl`
   - Creates new run record with status `PROCESSING`, currentStage `0`
   - Document name suffixed with " (rerun)" to distinguish from original
   - Triggers Railway backend with same parameters as original run

4. **Backend Pipeline Trigger**
   - POST to `${NEXT_PUBLIC_BACKEND_URL}/api/pipeline/run`
   - Payload: `{ run_id: newRunId, blob_url: documentUrl, company_id: companyId, user_id: userId }`
   - If trigger fails → Update run status to `FAILED`, show error message to user
   - If trigger succeeds → Redirect user to pipeline viewer with polling enabled

5. Original run remains unchanged (no modifications to existing run record)

6. New run appears in sidebar "My Runs" section immediately

7. Railway backend processes rerun identically to new run

8. Clerk authentication verifies user owns original run before allowing rerun

9. Optimistic UI: Rerun button shows loading spinner during API call

10. Error handling: If rerun fails, show error toast with retry option

11. Success feedback: Toast notification "Rerun started" before navigation

12. Rerun preserves exact same Vercel Blob URL (no re-upload required)

### Tasks / Subtasks

- [ ] Add rerun button to run detail page (AC: 1)
  - [ ] Add "Rerun" button to page header
  - [ ] Create confirmation modal component
  - [ ] Implement onClick handler

- [ ] Add rerun button to run history cards (AC: 2)
  - [ ] Add "Rerun" button to RunCard component
  - [ ] Reuse confirmation modal
  - [ ] Implement onClick handler

- [ ] Create rerun API endpoint (AC: 3, 4, 5)
  - [ ] Create `app/api/runs/[runId]/rerun/route.ts`
  - [ ] Fetch original run parameters from database
  - [ ] Create new run record with "(rerun)" suffix
  - [ ] Trigger Railway backend POST request
  - [ ] Handle backend trigger failures
  - [ ] Verify user ownership with Clerk

- [ ] Implement backend integration (AC: 4, 7)
  - [ ] Create Railway API call function
  - [ ] Build payload with run_id, blob_url, company_id, user_id
  - [ ] Handle successful trigger → redirect to pipeline viewer
  - [ ] Handle failed trigger → update run status to FAILED

- [ ] Add UI feedback (AC: 9, 10, 11)
  - [ ] Add loading spinner to rerun button
  - [ ] Create error toast with retry option
  - [ ] Create success toast notification
  - [ ] Implement navigation after successful rerun

- [ ] Ensure data integrity (AC: 5, 6, 8, 12)
  - [ ] Verify original run unchanged
  - [ ] Test new run appears in sidebar immediately
  - [ ] Verify Clerk auth checks ownership
  - [ ] Confirm Vercel Blob URL preserved

- [ ] Write integration tests (DoD)
  - [ ] Test rerun creates independent run record
  - [ ] Test Railway backend receives correct payload
  - [ ] Test failed reruns marked as FAILED
  - [ ] Test original run remains unchanged
  - [ ] Test user authorization enforcement

### Dev Notes

**Existing System Integration:**
- Integrates with: Existing pipeline creation flow and Railway backend
- Technology: Prisma create operation, Railway API trigger, Next.js API routes
- Follows pattern: Same flow as initial run creation (POST `/api/runs`)
- Touch points: Railway backend `/api/pipeline/run` endpoint, Run detail page UI, Run history page UI

**API Implementation:** See PRD lines 1619-1703

**Prisma Operations:**
```typescript
// Fetch original run
const originalRun = await prisma.run.findFirst({
  where: { id: runId, user: { clerkId: userId } }
})

// Create new run
const newRun = await prisma.run.create({
  data: {
    userId: originalRun.userId,
    companyId: originalRun.companyId,
    companyName: originalRun.companyName,
    documentName: `${originalRun.documentName} (rerun)`,
    documentUrl: originalRun.documentUrl,
    status: 'PROCESSING'
  }
})
```

**Railway Backend Call:**
```typescript
await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/pipeline/run`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    run_id: newRun.id,
    blob_url: originalRun.documentUrl,
    company_id: originalRun.companyId,
    user_id: originalRun.userId
  })
})
```

**Error Handling:** If backend fails, mark new run as FAILED and update errorMessage field

**Component Location:**
- `innovation-web/src/app/api/runs/[runId]/rerun/route.ts` (new)
- Update `innovation-web/src/app/runs/[runId]/page.tsx`
- Update `innovation-web/src/components/RunCard.tsx`

#### Testing

**Test File Location:**
- `innovation-web/src/app/api/runs/[runId]/rerun/__tests__/route.test.ts`

**Testing Standards:**
- Use Jest for API route testing
- Mock Railway backend API calls
- Mock Prisma database operations
- Test Clerk authentication
- Verify error handling paths

**Testing Framework:** Jest + Prisma mock + fetch mock

**Specific Testing Requirements:**
- Test rerun creates new run with correct parameters
- Test document name includes "(rerun)" suffix
- Test Railway backend receives correct payload
- Test failed backend trigger marks run as FAILED
- Test original run remains unchanged
- Test unauthorized user cannot rerun
- Test optimistic UI updates correctly
- Test error toast displays on failure

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.5: Delete Run with Cascade

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to delete old or unwanted pipeline runs,
**so that** I can keep my run history clean and focused on relevant analyses.

### Acceptance Criteria

1. **Delete Button - Run Detail Page**
   - "Delete Run" button in page header (top-right, styled as destructive)
   - Click → Show confirmation modal with warning message
   - Modal text: "Delete this run? This will permanently remove the run and all {cardCount} opportunity cards. This action cannot be undone."
   - Cancel button → Close modal, no action
   - Confirm button → DELETE `/api/runs/[runId]`, redirect to `/runs` on success

2. **Delete Button - Run History Page**
   - Each run card has "Delete" action (icon or text button)
   - Click → Same confirmation modal as above
   - Confirm → DELETE `/api/runs/[runId]`, remove card from grid immediately (optimistic update)

3. **API Behavior**
   - Endpoint: `DELETE /api/runs/[runId]`
   - Verifies user owns run via Clerk auth
   - Uses Prisma `deleteMany` with user ID constraint
   - Returns 404 if run not found or user unauthorized
   - Returns 200 with `{ success: true }` on successful deletion

4. **Cascade Delete Behavior**
   - Deleting run automatically deletes:
     - All related `OpportunityCard` records
     - Related `InspirationReport` record
     - All related `StageOutput` records
   - Cascade defined in Prisma schema: `@relation(onDelete: Cascade)`
   - All deletes execute in single atomic transaction (ACID guarantee)

5. Deletion removes run from sidebar "My Runs" section immediately

6. If user deletes run while viewing it, redirect to `/runs` after success

7. Run history page updates count and grid after deletion

8. Existing runs remain unchanged (no side effects)

9. Confirmation modal prevents accidental deletions

10. Optimistic UI: Card disappears immediately, reverts if API fails

11. Error handling: If delete fails, show error toast and restore card

12. Loading state: Delete button shows spinner during API call

### Tasks / Subtasks

- [ ] Add delete button to run detail page (AC: 1)
  - [ ] Add "Delete Run" button to page header with destructive styling
  - [ ] Create confirmation modal component
  - [ ] Add modal text with dynamic card count
  - [ ] Implement confirm/cancel handlers
  - [ ] Add redirect to `/runs` on success

- [ ] Add delete button to run history cards (AC: 2)
  - [ ] Add "Delete" button to RunCard component
  - [ ] Reuse confirmation modal
  - [ ] Implement optimistic UI update

- [ ] Create delete API endpoint (AC: 3, 4)
  - [ ] Create `app/api/runs/[runId]/route.ts` with DELETE handler
  - [ ] Verify user ownership with Clerk
  - [ ] Use Prisma deleteMany with user constraint
  - [ ] Handle 404 for non-existent or unauthorized runs
  - [ ] Return success response

- [ ] Configure Prisma cascade relations (AC: 4)
  - [ ] Verify schema has @relation(onDelete: Cascade) for all relations
  - [ ] Test cascade deletes all related records
  - [ ] Ensure atomic transaction (ACID)

- [ ] Implement UI feedback (AC: 5, 6, 7, 9, 10, 11, 12)
  - [ ] Update sidebar to remove deleted run
  - [ ] Add redirect logic from detail page
  - [ ] Update history page count and grid
  - [ ] Implement optimistic UI with revert on error
  - [ ] Add loading spinner to delete button
  - [ ] Create error toast with restore option

- [ ] Write integration tests (DoD)
  - [ ] Test cascade delete removes all related records
  - [ ] Test user authorization enforcement
  - [ ] Test 404 handling
  - [ ] Test optimistic UI revert on error
  - [ ] Verify no orphaned records in database

### Dev Notes

**Existing System Integration:**
- Integrates with: Run detail page and run history page
- Technology: Prisma cascade delete, Next.js API routes, shadcn/ui Dialog
- Follows pattern: Delete confirmation modal pattern (common in admin interfaces)
- Touch points: `/api/runs/[runId]` DELETE endpoint, Prisma cascade relations

**API Implementation:** See PRD lines 1705-1729

**Prisma Delete Pattern:**
```typescript
const deleted = await prisma.run.deleteMany({
  where: {
    id: runId,
    user: { clerkId: userId }
  }
})

if (deleted.count === 0) {
  return NextResponse.json({ error: 'Run not found' }, { status: 404 })
}
```

**Cascade Relations (from Prisma Schema):**
```prisma
model Run {
  opportunityCards  OpportunityCard[]  @relation(onDelete: Cascade)
  inspirationReport InspirationReport? @relation(onDelete: Cascade)
  stageOutputs      StageOutput[]      @relation(onDelete: Cascade)
}
```

**shadcn/ui Components:**
- `AlertDialog` for delete confirmation
- `Button` variant="destructive" for delete action

**Component Location:**
- `innovation-web/src/app/api/runs/[runId]/route.ts` (new DELETE handler)
- Update `innovation-web/src/app/runs/[runId]/page.tsx`
- Update `innovation-web/src/components/RunCard.tsx`

#### Testing

**Test File Location:**
- `innovation-web/src/app/api/runs/[runId]/__tests__/route.test.ts`

**Testing Standards:**
- Use Jest for API route testing
- Mock Prisma database operations
- Test cascade delete behavior
- Verify ACID transaction properties
- Test Clerk authentication

**Testing Framework:** Jest + Prisma mock

**Specific Testing Requirements:**
- Test delete endpoint removes run and all related records
- Test unauthorized user cannot delete
- Test 404 returned for non-existent run
- Test optimistic UI reverts on API failure
- Test confirmation modal prevents accidental deletion
- Verify no orphaned records after cascade delete
- Test redirect works from detail page
- Test history page updates after deletion

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.6: Star/Favorite Opportunity Cards

### Status
Draft

### Story
**As a** product innovation manager,
**I want** to star/bookmark specific opportunity cards that I find most promising,
**so that** I can quickly identify and revisit my favorite innovation concepts across multiple runs.

### Acceptance Criteria

1. **Star Button on Cards**
   - Star icon button appears in top-right corner of every opportunity card
   - Unstarred state: Outline star icon (☆) with gray color
   - Starred state: Filled star icon (⭐) with yellow color
   - Click → Toggle starred state via POST `/api/cards/[cardId]/star`

2. **Star Locations**
   - Results page: All 5 opportunity cards display star button
   - Run detail page (Opportunity Cards tab): All cards display star button
   - Card modal/expansion: Star button visible in modal header

3. **API Behavior**
   - Endpoint: `POST /api/cards/[cardId]/star`
   - Verifies user owns card via Clerk auth
   - Toggles `starred` boolean field: `true → false` or `false → true`
   - Returns new state: `{ starred: true }` or `{ starred: false }`
   - Returns 404 if card not found or user unauthorized

4. **Persistence**
   - Starred state persists across sessions (stored in database)
   - User sees same starred cards when returning to run detail page
   - Starred cards remain starred even after logout/login

5. Existing card rendering logic continues to work unchanged

6. Star state updates immediately without full page refresh

7. Multiple stars can be toggled in quick succession without conflicts

8. Star state visible on both results page and run detail page

9. Optimistic UI: Icon updates immediately on click (before API response)

10. Error handling: Reverts to previous state if API call fails

11. Loading state: Subtle animation during API call (optional)

12. Accessibility: Star button has aria-label "Toggle favorite" for screen readers

### Tasks / Subtasks

- [ ] Add star button to opportunity cards (AC: 1, 2)
  - [ ] Add star icon button to OpportunityCard component
  - [ ] Style filled vs outline star icons with colors
  - [ ] Position button in top-right corner
  - [ ] Add star button to results page cards
  - [ ] Add star button to run detail page cards
  - [ ] Add star button to card modal header

- [ ] Create star toggle API endpoint (AC: 3)
  - [ ] Create `app/api/cards/[cardId]/star/route.ts`
  - [ ] Fetch card and verify user ownership
  - [ ] Toggle starred boolean field
  - [ ] Return new state in response
  - [ ] Handle 404 for unauthorized access

- [ ] Implement star toggle functionality (AC: 5, 6, 7, 9, 10)
  - [ ] Create onClick handler for star button
  - [ ] Implement optimistic UI update
  - [ ] Call POST `/api/cards/[cardId]/star`
  - [ ] Sync with server response
  - [ ] Add error handling with state revert
  - [ ] Show error toast on failure

- [ ] Ensure persistence (AC: 4, 8)
  - [ ] Verify starred field stored in database
  - [ ] Test state persists across page refreshes
  - [ ] Test state persists across sessions
  - [ ] Verify state visible on all card locations

- [ ] Add accessibility and polish (AC: 11, 12)
  - [ ] Add aria-label to star button
  - [ ] Add optional loading animation
  - [ ] Match brutalist aesthetic

- [ ] Write unit and integration tests (DoD)
  - [ ] Test star toggle updates database
  - [ ] Test optimistic UI behavior
  - [ ] Test error handling and revert
  - [ ] Test persistence across sessions
  - [ ] Test accessibility with screen readers

### Dev Notes

**Existing System Integration:**
- Integrates with: Opportunity card rendering components, run detail page
- Technology: Prisma update operation, Next.js API routes, React state management
- Follows pattern: Toggle button with optimistic UI updates
- Touch points: `/api/cards/[cardId]/star` endpoint, OpportunityCard component

**API Implementation:** See PRD lines 1730-1798 and architecture doc lines 546-599

**Prisma Update Pattern:**
```typescript
// Fetch card to verify ownership
const card = await prisma.opportunityCard.findFirst({
  where: {
    id: cardId,
    user: { clerkId: userId }
  }
})

// Toggle starred field
const updatedCard = await prisma.opportunityCard.update({
  where: { id: cardId },
  data: { starred: !card.starred }
})

return NextResponse.json({ starred: updatedCard.starred })
```

**React State Management:**
```typescript
const [starred, setStarred] = useState(card.starred)

const handleStarClick = async () => {
  // Optimistic update
  setStarred(!starred)

  try {
    const res = await fetch(`/api/cards/${cardId}/star`, { method: 'POST' })
    const data = await res.json()
    setStarred(data.starred) // Sync with server response
  } catch (error) {
    // Revert on error
    setStarred(starred)
    toast.error('Failed to update favorite')
  }
}
```

**Component Location:**
- `innovation-web/src/app/api/cards/[cardId]/star/route.ts` (new)
- Update `innovation-web/src/components/OpportunityCard.tsx`
- Update `innovation-web/src/app/results/page.tsx` (if needed)
- Update `innovation-web/src/app/runs/[runId]/page.tsx` (if needed)

#### Testing

**Test File Location:**
- `innovation-web/src/app/api/cards/[cardId]/star/__tests__/route.test.ts`
- `innovation-web/src/components/__tests__/OpportunityCard.test.tsx`

**Testing Standards:**
- Use React Testing Library for component tests
- Use Jest for API route testing
- Mock Prisma database operations
- Test optimistic UI behavior
- Test error handling paths

**Testing Framework:** Jest + React Testing Library + Prisma mock

**Specific Testing Requirements:**
- Test star button renders in all locations
- Test click toggles between filled and outline icon
- Test API updates starred field in database
- Test optimistic UI updates immediately
- Test error reverts icon on API failure
- Test starred state persists across page refresh
- Test user can only star their own cards
- Test ARIA label for accessibility
- Test multiple rapid toggles don't cause conflicts

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

---

## Story 1.7: Prisma Database Setup & Migration

### Status
Draft

### Story
**As a** developer,
**I want** to set up PostgreSQL database with Prisma ORM and run initial migrations,
**so that** the application can persist user runs and opportunity cards.

### Acceptance Criteria

1. **Database Provisioning**
   - Create PostgreSQL database on Railway
   - Obtain connection string: `postgresql://user:password@host:port/database`
   - Add `DATABASE_URL` to Vercel environment variables (production)
   - Add `DATABASE_URL` to `.env.local` (local development)

2. **Prisma Schema Setup**
   - Create `prisma/schema.prisma` with complete schema (PRD lines 1150-1275)
   - Define models: `User`, `Run`, `OpportunityCard`, `InspirationReport`, `StageOutput`
   - Define enum: `RunStatus` (PROCESSING, COMPLETED, FAILED, CANCELLED)
   - Configure indexes for common queries: `[userId, createdAt]`, `[clerkId]`, `[status]`

3. **Prisma Client Singleton**
   - Create `lib/prisma.ts` with singleton pattern (PRD lines 1295-1312)
   - Prevent multiple Prisma Client instances in serverless environment
   - Enable query logging in development mode

4. **Initial Migration**
   - Run `npx prisma migrate dev --name init` to create migration
   - Verify migration creates all tables with correct columns
   - Check indexes and foreign keys created correctly
   - Seed database with test user (optional, for local development)

5. **Prisma Client Generation**
   - Run `npx prisma generate` to create TypeScript types
   - Verify type definitions generated in `node_modules/@prisma/client`
   - Ensure TypeScript autocomplete works for all models

6. Railway database accessible from Vercel deployment

7. Connection pooling configured for serverless (default Prisma behavior)

8. Environment variables secured (not committed to git)

9. `.env.example` file documents required environment variables

10. Migration runs successfully without errors

11. Rollback script created for safe schema changes

12. Database credentials stored securely (Railway secrets, Vercel env vars)

13. Documentation updated with setup instructions

### Tasks / Subtasks

- [ ] Provision PostgreSQL database (AC: 1)
  - [ ] Create PostgreSQL database on Railway
  - [ ] Obtain connection string
  - [ ] Add DATABASE_URL to Vercel environment variables
  - [ ] Add DATABASE_URL to .env.local
  - [ ] Create .env.example file

- [ ] Create Prisma schema (AC: 2)
  - [ ] Create prisma/schema.prisma file
  - [ ] Define User model
  - [ ] Define Run model with RunStatus enum
  - [ ] Define OpportunityCard model
  - [ ] Define InspirationReport model
  - [ ] Define StageOutput model
  - [ ] Add indexes for common queries
  - [ ] Configure cascade delete relations

- [ ] Create Prisma singleton (AC: 3)
  - [ ] Create lib/prisma.ts file
  - [ ] Implement singleton pattern for serverless
  - [ ] Enable query logging in development

- [ ] Run initial migration (AC: 4)
  - [ ] Run npx prisma migrate dev --name init
  - [ ] Verify all tables created correctly
  - [ ] Verify indexes created correctly
  - [ ] Verify foreign keys created correctly
  - [ ] Create optional seed script

- [ ] Generate Prisma Client (AC: 5)
  - [ ] Run npx prisma generate
  - [ ] Verify TypeScript types generated
  - [ ] Test autocomplete in IDE

- [ ] Configure Vercel build (AC: 6, 7)
  - [ ] Update package.json with postinstall script
  - [ ] Update build script to run prisma generate
  - [ ] Test connection from Vercel to Railway
  - [ ] Verify connection pooling works

- [ ] Secure credentials (AC: 8, 9, 12)
  - [ ] Ensure .env.local in .gitignore
  - [ ] Document required env vars in .env.example
  - [ ] Store credentials in Railway secrets
  - [ ] Store credentials in Vercel env vars

- [ ] Create rollback script (AC: 11)
  - [ ] Document rollback procedure
  - [ ] Test rollback with sample migration

- [ ] Update documentation (AC: 13)
  - [ ] Document database setup instructions
  - [ ] Document migration commands
  - [ ] Document Prisma Studio usage
  - [ ] Document troubleshooting steps

### Dev Notes

**Existing System Integration:**
- Integrates with: Vercel deployment, Railway backend, Next.js API routes
- Technology: Prisma ORM, PostgreSQL (Railway-hosted), Vercel environment variables
- Follows pattern: Standard Prisma setup for serverless Next.js (PRD section 4.6.3)
- Touch points: All API routes that query/mutate database

**Prisma Schema Location:** `prisma/schema.prisma`

**Complete Schema:** See PRD lines 1150-1275

**Singleton Pattern:** See PRD lines 1295-1312

**Migration Commands:**
```bash
# Create migration
npx prisma migrate dev --name init

# Apply migration to production
npx prisma migrate deploy

# Generate Prisma Client
npx prisma generate

# Open Prisma Studio (database GUI)
npx prisma studio
```

**Environment Variables:**
```env
# .env.local (local development)
DATABASE_URL="postgresql://user:password@localhost:5432/innovation_db"

# Vercel (production)
DATABASE_URL="postgresql://user:password@railway.host:5432/innovation_db"
```

**Vercel Build Configuration:**
```json
// package.json
{
  "scripts": {
    "postinstall": "prisma generate",
    "build": "prisma generate && next build"
  }
}
```

**Files to Create:**
- `prisma/schema.prisma`
- `lib/prisma.ts`
- `.env.example`

#### Testing

**Test File Location:**
- `innovation-web/__tests__/prisma-setup.test.ts`

**Testing Standards:**
- Verify database connection works
- Test Prisma Client singleton pattern
- Verify all models accessible
- Test migration rollback procedure

**Testing Framework:** Jest + Prisma

**Specific Testing Requirements:**
- Test DATABASE_URL environment variable configured
- Test Prisma Client instantiation
- Test database connection from Next.js
- Verify all tables exist in database
- Verify indexes created correctly
- Verify foreign keys configured properly
- Test migration rollback works
- Verify no connection leaks in serverless

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-21 | 1.0 | Initial story creation from epic | John (PM) |

### Dev Agent Record

#### Agent Model Used
_To be populated by dev agent_

#### Debug Log References
_To be populated by dev agent_

#### Completion Notes List
_To be populated by dev agent_

#### File List
_To be populated by dev agent_

### QA Results
_To be populated by QA agent_

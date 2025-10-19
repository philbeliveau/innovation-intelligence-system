# 8. Testing Strategy

## 8.1 Manual Testing (Hackathon Scope)

**Test Case 1: Happy Path**
1. Navigate to homepage
2. Upload `savannah-bananas.pdf`
3. Select "Lactalis Canada"
4. Click "Generate Opportunities"
5. Verify redirect to `/pipeline/run-*`
6. Verify Stage 1 shows 2 inspiration tracks after 3-5 minutes
7. Verify Stages 2-5 update status icons
8. Verify redirect to results page when complete
9. Verify 5 opportunity cards display correctly

**Test Case 2: Invalid File Upload**
1. Upload `.exe` file → Expect error message
2. Upload 50MB PDF → Expect "File too large" error

**Test Case 3: Missing Brand Selection**
1. Upload valid PDF
2. Do not select brand
3. Click "Generate" → Expect button disabled

**Test Case 4: Pipeline Failure**
1. Upload corrupted PDF
2. Verify error status in `/api/status` response
3. Verify frontend displays error message

## 8.2 Automated Testing (Phase 2 - Out of Scope)

- Unit tests for API routes (Jest)
- Component tests (React Testing Library)
- E2E tests (Playwright)
- Load testing (k6)

---

# 5. Non-Functional Requirements

## 5.1 Performance

**NFR-P-1: Upload Speed**
- File upload to Blob: < 5 seconds for 10MB file
- API response time: < 2 seconds for all endpoints (except /run which is background)

**NFR-P-2: Pipeline Execution**
- Stage 1: 3-5 minutes
- Stage 2: 2-4 minutes
- Stage 3: 2-4 minutes
- Stage 4: 3-5 minutes
- Stage 5: 4-6 minutes
- **Total: 15-30 minutes**

**NFR-P-3: UI Responsiveness**
- Status polling interval: 5 seconds
- No UI freezing during polling
- Skeleton loading states for async data

## 5.2 Reliability

**NFR-R-1: Error Recovery**
- If pipeline crashes, log error and set status to "error"
- Frontend displays error message with support contact
- No silent failures

**NFR-R-2: Data Persistence**
- All run outputs saved to filesystem: `data/test-outputs/{run_id}/`
- Logs preserved for debugging
- Files retained for 7 days (manual cleanup for hackathon)

## 5.3 Scalability (Post-Hackathon)

**NFR-S-1: Concurrent Runs**
- Hackathon: 1 run at a time (no queue)
- Phase 2: Support 5 concurrent runs via queue system

**NFR-S-2: Storage**
- Hackathon: No cleanup (manual deletion)
- Phase 2: Auto-delete runs older than 30 days

## 5.4 Security

**NFR-SEC-1: File Validation**
- Only allow PDF, TXT, MD uploads
- Scan for malicious content (Phase 2)
- 25MB size limit enforced

**NFR-SEC-2: API Security**
- No authentication (public access for hackathon)
- Phase 2: Add API keys and rate limiting

**NFR-SEC-3: Environment Variables**
- Store sensitive credentials in `.env.local`:
  - `OPENROUTER_API_KEY`
  - `BLOB_READ_WRITE_TOKEN`
  - `LLM_MODEL`

## 5.5 Usability

**NFR-U-1: Browser Support**
- Chrome/Edge: Latest 2 versions
- Safari: Latest version
- Firefox: Latest version
- Mobile: Not optimized (Phase 2)

**NFR-U-2: Accessibility**
- Keyboard navigation supported
- Screen reader compatibility (basic)
- WCAG 2.1 AA compliance (Phase 2)

---

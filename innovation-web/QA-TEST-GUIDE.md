# QA Test Guide - Story 1.2: File Upload to Vercel Blob

## Setup (5 minutes)

### 1. Environment Configuration

The `.env.local` file is already configured with the Blob token:
```bash
BLOB_READ_WRITE_TOKEN="vercel_blob_rw_FdT3gMiQrtfo2aCZ_xI5LU5CRc4bjQnnL6epgxjDdgROHic"
```

✅ **No action needed** - token is ready to use.

### 2. Start Development Server

```bash
cd innovation-web
npm run dev
```

**Expected output:**
```
▲ Next.js 15.5.6
- Local:        http://localhost:3000 (or 3001 if port 3000 is in use)
✓ Ready in ~800ms
```

**Note:** If server uses port 3001, adjust all test URLs accordingly.

---

## Test Execution (15 minutes)

### Test 1: Valid PDF Upload ✅

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@../documentation/document/savannah-bananas.pdf" | jq .
```

**Expected Response (200):**
```json
{
  "upload_id": "upload-1729349025123",
  "blob_url": "https://[blob-storage-url]/uploads/1729349025123-savannah-bananas.pdf",
  "file_name": "savannah-bananas.pdf",
  "file_size": 146432,
  "uploaded_at": "2025-10-19T14:23:45.123Z"
}
```

**Validation Checklist:**
- [ ] HTTP status code is 200
- [ ] `upload_id` format matches `upload-{timestamp}`
- [ ] `blob_url` is a valid HTTPS URL
- [ ] `file_name` matches uploaded file
- [ ] `file_size` is in bytes (should be ~143KB = 146432 bytes)
- [ ] `uploaded_at` is valid ISO 8601 timestamp

---

### Test 2: Verify Blob URL is Publicly Accessible ✅

**Command:**
```bash
# Use the blob_url from Test 1 response
curl -I "<blob_url_from_test_1>"
```

**Expected Response:**
```
HTTP/2 200
content-type: application/pdf
content-length: 146432
```

**Validation Checklist:**
- [ ] HTTP status code is 200
- [ ] Content-Type matches file type (application/pdf)
- [ ] File is accessible without authentication

---

### Test 3: Valid Text File Upload ✅

**Setup:**
```bash
cd /tmp
echo "Test content for innovation pipeline" > test.txt
```

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/test.txt;type=text/plain" | jq .
```

**Expected Response (200):**
```json
{
  "upload_id": "upload-...",
  "blob_url": "https://...",
  "file_name": "test.txt",
  "file_size": 37,
  "uploaded_at": "..."
}
```

**Validation Checklist:**
- [ ] HTTP 200 response
- [ ] File successfully uploaded
- [ ] Response structure matches specification

---

### Test 4: Valid Markdown File Upload ✅

**Setup:**
```bash
cd /tmp
echo "# Innovation Report\n\nTest markdown content" > test.md
```

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/test.md;type=text/markdown" | jq .
```

**Expected Response (200):**
```json
{
  "upload_id": "upload-...",
  "blob_url": "https://...",
  "file_name": "test.md",
  "file_size": 42,
  "uploaded_at": "..."
}
```

**Validation Checklist:**
- [ ] HTTP 200 response
- [ ] Markdown file accepted
- [ ] Blob URL accessible

---

### Test 5: Invalid File Type (Reject .exe) ❌

**Setup:**
```bash
cd /tmp
echo "fake executable" > test.exe
```

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/test.exe" | jq .
```

**Expected Response (400):**
```json
{
  "error": "Invalid file type"
}
```

**Validation Checklist:**
- [ ] HTTP status code is 400
- [ ] Error message exactly matches: "Invalid file type"
- [ ] File was NOT uploaded to Blob storage

---

### Test 6: Oversized File (Reject >25MB) ❌

**Setup:**
```bash
cd /tmp
dd if=/dev/zero of=oversized.pdf bs=1M count=30
```

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/oversized.pdf;type=application/pdf" | jq .
```

**Expected Response (400):**
```json
{
  "error": "File too large (max 25MB)"
}
```

**Validation Checklist:**
- [ ] HTTP status code is 400
- [ ] Error message exactly matches: "File too large (max 25MB)"
- [ ] File was NOT uploaded to Blob storage
- [ ] Response time < 2 seconds (size check before upload)

---

### Test 7: Missing File Field ❌

**Command:**
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "notfile=dummy" | jq .
```

**Expected Response (400):**
```json
{
  "error": "No file provided"
}
```

**Validation Checklist:**
- [ ] HTTP status code is 400
- [ ] Error message exactly matches: "No file provided"

---

### Test 8: Performance Test (10MB file) ⏱️

**Setup:**
```bash
cd /tmp
dd if=/dev/zero of=10mb.pdf bs=1M count=10
```

**Command:**
```bash
time curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/10mb.pdf;type=application/pdf" | jq .
```

**Expected:**
- [ ] Upload completes in < 5 seconds
- [ ] HTTP 200 response
- [ ] Valid blob URL returned

---

### Test 9: Concurrent Upload Test 🔄

**Command (run in 3 separate terminals simultaneously):**

Terminal 1:
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@../documentation/document/savannah-bananas.pdf" | jq .
```

Terminal 2:
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/test.txt;type=text/plain" | jq .
```

Terminal 3:
```bash
curl -X POST http://localhost:3000/api/upload \
  -F "file=@/tmp/test.md;type=text/markdown" | jq .
```

**Expected:**
- [ ] All 3 uploads succeed (HTTP 200)
- [ ] Each gets unique upload_id
- [ ] No file locking errors
- [ ] No race conditions

---

### Test 10: Retry Logic Verification 🔁

**Check server logs during Test 1-4:**
```bash
# In separate terminal, monitor server logs
tail -f /tmp/nextjs-dev.log
```

**With VALID token:**
- [ ] No retry attempts logged (upload succeeds on first attempt)

**To test retry logic (optional - requires breaking the token):**
1. Temporarily corrupt `BLOB_READ_WRITE_TOKEN` in `.env.local`
2. Restart dev server
3. Attempt upload
4. Check logs for: "Upload attempt 1 failed", "Retrying in 1000ms", "Upload attempt 2 failed", "Retrying in 2000ms", etc.
5. Restore correct token

---

### Test 11: Python CLI Regression Test 🐍

**Command:**
```bash
cd ..
export PYTHONPATH=.
python scripts/run_pipeline.py --help
```

**Expected Output:**
```
usage: run_pipeline.py [-h] [--input INPUT] [--brand BRAND] [--batch]
                       [--retry-failed] [--verbose]

Innovation Intelligence Pipeline - Process input documents to generate brand-specific innovation opportunities
...
```

**Validation Checklist:**
- [ ] Python CLI still works unchanged
- [ ] No errors loading pipeline modules
- [ ] No breaking changes introduced

---

## Test Results Summary

### Total Tests: 11

**Pass Criteria:**
- All validation tests (1-7) must pass
- Performance test (8) must complete < 5 seconds
- Concurrent test (9) must succeed
- CLI regression (11) must pass

**Test Execution Checklist:**
- [ ] Test 1: Valid PDF upload (200)
- [ ] Test 2: Blob URL publicly accessible (200)
- [ ] Test 3: Valid TXT upload (200)
- [ ] Test 4: Valid MD upload (200)
- [ ] Test 5: Invalid file type rejected (400)
- [ ] Test 6: Oversized file rejected (400)
- [ ] Test 7: Missing file rejected (400)
- [ ] Test 8: Performance < 5 seconds
- [ ] Test 9: Concurrent uploads successful
- [ ] Test 10: Retry logic (optional verification)
- [ ] Test 11: Python CLI unchanged

---

## Acceptance Criteria Coverage

This test suite validates all 30 acceptance criteria from Story 1.2:

- **AC 1-3:** API route structure and response format
- **AC 4-9:** File validation (type, size, errors)
- **AC 10-12:** Blob storage configuration
- **AC 13-18:** Upload ID generation and tracking
- **AC 19-27:** Error handling and retry logic
- **AC 28-30:** Performance and concurrency

---

## Troubleshooting

**Issue:** Server starts on port 3001 instead of 3000
- **Solution:** Update all test URLs to use port 3001

**Issue:** Token error "Access denied"
- **Solution:** Verify `.env.local` contains correct `BLOB_READ_WRITE_TOKEN`

**Issue:** `jq` command not found
- **Solution:** Install jq: `brew install jq` OR remove `| jq .` from commands

**Issue:** Test files not found
- **Solution:** Verify file paths are correct relative to `innovation-web/` directory

---

## Sign-off

**QA Engineer:** _______________
**Date:** _______________
**Result:** [ ] PASS / [ ] FAIL
**Comments:**

---

**Story 1.2 Status:** Ready for Review
**Developer:** James (Dev Agent)
**Implementation Date:** 2025-10-19

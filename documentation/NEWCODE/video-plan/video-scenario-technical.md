# Video Scenario: Technical Version
## "Debugging 405 Errors Across FastAPI + Next.js Stack with Claude MCP"

**Video Series:** Newcode - Subject 1: FastAPI MCP Debugging
**Target Audience:** Developers, technical managers, DevOps engineers
**Duration:** 5-7 minutes
**Difficulty:** Intermediate

---

## 🎯 Learning Objectives

By the end of this video, viewers will understand:

1. How to debug **multi-system errors** (Python backend → Next.js API → Database)
2. Using **FastAPI MCP** to analyze Railway logs and Python code
3. Using **Vercel MCP** to diagnose deployment issues
4. **Real-world debugging workflow** in a modern full-stack application
5. The importance of **verifying production deployments** after code changes

---

## 📋 Pre-Recording Setup

### Environment State:
- ✅ Railway backend deployed with Prisma integration code
- ✅ Vercel frontend deployed (but possibly with **old code** missing new API routes)
- ✅ Test document ready (savannah-bananas.pdf or similar)
- ✅ Railway logs showing 405 errors
- ✅ Database showing PipelineRun stuck at PROCESSING status

### Required Access:
- Railway dashboard (logs access)
- Vercel dashboard (deployment management)
- Prisma Studio (database inspection)
- Claude Code with MCP tools enabled

### Test Data:
- Company: Lactalis Canada
- Document: Savannah Bananas report
- Expected behavior: 5-stage pipeline completes, generates 5 opportunity cards
- Actual behavior: Pipeline completes, but database never updates (stuck at PROCESSING)

---

## 🎬 Video Script

### **[0:00-0:30] Hook - The Problem**

**Screen Recording:**
- Browser showing innovation app
- Upload document, click "Analyze"
- Progress indicator appears: "Stage 1 Processing..."
- Wait 3 minutes... still shows "Stage 1 Processing..."
- Check Railway logs in split screen → "Pipeline execution completed successfully"
- **Contradiction:** Backend says complete, frontend says processing

**Narration:**
> "The pipeline just completed successfully—all 5 stages, generated opportunity cards. But the frontend is stuck showing 'Processing' forever. And if I check the database..."

**Switch to Prisma Studio:**
- Show PipelineRun table
- Status: PROCESSING (should be COMPLETED)
- completedAt: null (should be timestamp)
- StageOutput table: empty (should have 5 rows)

**Narration:**
> "The database never got updated. Railway logs show repeated 405 errors every time the backend tries to update Prisma. Let's debug this with Claude Code."

---

### **[0:30-1:15] Initial Investigation with Claude**

**Screen Recording:**
- Open Claude Code
- Copy Railway logs showing 405 errors
- Paste into Claude with context:

**Typed prompt:**
```
I'm getting 405 errors when my Python backend tries to update stage progress via the Next.js Prisma API.

Railway logs:
[paste logs with 405 errors]

The backend is calling POST /api/pipeline/{runId}/stage-update
But getting 405 Method Not Allowed on every request.

Context: Just refactored from file-based status to Prisma-first architecture.
See backend/PRISMA_INTEGRATION.md for migration details.
```

**Narration:**
> "I'm giving Claude the error logs and context about our recent architecture refactor. 405 means 'Method Not Allowed'—the endpoint exists but doesn't support the HTTP method we're using... or doesn't exist at all."

**Claude's Response (show on screen):**
- Acknowledges 405 error pattern
- Asks to see the backend code making the requests
- Asks to see the frontend API route definition

---

### **[1:15-2:30] Cross-System Investigation**

**Screen Recording (split screen):**
- Left: Claude Code conversation
- Right: File explorer showing repo structure

**Claude reads files:**

**File 1: Backend calling the API**
```python
# backend/app/prisma_client.py
```

**Claude analysis (show text on screen):**
> "Backend is calling: POST /api/pipeline/{runId}/stage-update ✓
> Payload includes: stageNumber, stageName, status, output ✓
> Uses X-Webhook-Secret header for auth ✓"

**File 2: Frontend API route**
```typescript
// innovation-web/app/api/pipeline/[runId]/stage-update/route.ts
```

**Claude analysis:**
> "Frontend route EXISTS ✓
> Exports POST handler ✓
> Validates webhook secret ✓
> Uses Prisma upsert for StageOutput ✓"

**Narration:**
> "So the route exists locally, exports the POST method, and the backend is calling it correctly. So why 405?"

**Claude's hypothesis (show on screen):**
> "The route exists in your local codebase but may not be deployed to Vercel production. Let me check your deployment status."

---

### **[2:30-3:30] The Discovery - Deployment Mismatch**

**Screen Recording:**
- Claude uses Vercel MCP tool
- Shows deployment list
- Highlights timestamp of latest deployment

**Claude command:**
```
Using Vercel MCP: list_deployments for innovation-web
```

**Result shown:**
```
Latest Production Deployment:
- Date: 2025-10-24 14:32:15 UTC
- Commit: b936cc0 "feat(backend): implement Prisma-first architecture via HTTP API"
- Status: READY

API Routes Added (after this deployment):
- innovation-web/app/api/pipeline/[runId]/stage-update/route.ts (added 2025-10-25 09:15)
- innovation-web/app/api/pipeline/[runId]/complete/route.ts (added 2025-10-25 09:20)
```

**Claude analysis (highlight on screen):**
> "🔍 Found the issue:
> - Your latest Vercel deployment is from **Oct 24**
> - The new API routes were added **Oct 25** (today)
> - The routes exist locally but were never deployed to production
> - When Railway calls the endpoints, Vercel returns 405 because they don't exist"

**Narration:**
> "There it is. We added the routes locally, tested them, committed them... but never redeployed the frontend. Classic deployment mistake."

---

### **[3:30-4:15] Secondary Issue - Brand ID Bug**

**Screen Recording:**
- While reviewing logs, Claude spots another issue
- Highlight logs showing: "No research data found for brand unknown"

**Claude observation:**
```
I also notice in the logs:
"WARNING - No research data found for brand unknown"

But you uploaded for brand: lactalis-canada
```

**Claude reads code:**
```python
# backend/app/pipeline_runner.py:324
brand_id = brand_profile.get("brand_id", "unknown")
```

**Claude reads YAML:**
```yaml
# data/brand-profiles/lactalis-canada.yaml
id: lactalis-canada          # ← Field is "id", not "brand_id"
company_name: Lactalis Canada
```

**Claude's fix suggestion:**
```python
# Fix: Check both field names
brand_id = brand_profile.get("id", brand_profile.get("brand_id", "unknown"))
```

**Narration:**
> "While diagnosing the 405 error, Claude spotted a second bug: the brand YAML uses 'id' not 'brand_id', so research data never loads. Nice catch."

---

### **[4:15-5:30] The Fix**

**Screen Recording (split screen):**
- Terminal on left
- Browser on right

**Fix 1: Redeploy Frontend**
```bash
cd innovation-web
vercel --prod --yes
```

**Narration:**
> "First, redeploy the frontend with the new API routes."

**Show Vercel deployment progress:**
- Building...
- Deploying...
- Success! Deployment ready

**Fix 2: Update Backend Code**
```bash
# Edit backend/app/pipeline_runner.py line 324
# Change: brand_id = brand_profile.get("brand_id", "unknown")
# To: brand_id = brand_profile.get("id", brand_profile.get("brand_id", "unknown"))

git add backend/app/pipeline_runner.py
git commit -m "fix: use 'id' field for brand_id extraction"
```

**Fix 3: Redeploy Backend to Railway**
```bash
git push railway fix/prisma-405-errors-video:main
```

**Narration:**
> "And redeploy the backend with the brand ID fix."

---

### **[5:30-6:30] Verification - It Works**

**Screen Recording:**
- Upload same test document
- Watch progress indicator update in real-time

**Split screen:**
- Top: Browser showing "Stage 1... Stage 2... Stage 3... Stage 4... Stage 5... Complete!"
- Bottom-left: Railway logs showing SUCCESS messages
- Bottom-right: Prisma Studio showing database updating in real-time

**Railway logs (show scrolling):**
```
✅ [run-xxx] Successfully updated stage 1 in Prisma
✅ [run-xxx] Successfully updated stage 2 in Prisma
✅ [run-xxx] Successfully updated stage 3 in Prisma
✅ [run-xxx] Successfully updated stage 4 in Prisma
✅ [run-xxx] Successfully updated stage 5 in Prisma
✅ [run-xxx] Successfully notified frontend of completion
```

**Prisma Studio (show query results):**
```sql
SELECT * FROM "StageOutput" WHERE "runId" = 'run-xxx';
-- Returns 5 rows (stages 1-5, all COMPLETED)

SELECT status, "completedAt" FROM "PipelineRun" WHERE id = 'run-xxx';
-- status: COMPLETED
-- completedAt: 2025-10-25 16:45:23
```

**Narration:**
> "Perfect. The stages update in real-time, the database shows all 5 stages completed, and the run status is COMPLETED with a timestamp. Problem solved."

---

### **[6:30-7:00] Takeaways**

**Screen Recording:**
- Slide with bullet points (or just text overlay)

**Narration:**
> "Here's what we learned:
>
> **1. Multi-system debugging is complex**
> We had to investigate Python backend, TypeScript frontend API, and PostgreSQL database.
>
> **2. Claude MCP made it fast**
> FastAPI MCP read Railway logs and Python code. Vercel MCP checked deployment status. We switched between systems effortlessly.
>
> **3. Always verify production deployments**
> Code working locally doesn't mean it's deployed. This is the most common bug in modern web development.
>
> **4. Architecture refactors need testing**
> We just migrated from file-based to Prisma-first architecture. New patterns = new failure modes.
>
> **5. AI catches secondary bugs**
> While debugging the 405 error, Claude spotted the brand ID field mismatch. Two bugs fixed in one session.
>
> **Time saved:** This debugging session took 7 minutes. Without Claude, it would've taken 2-3 hours—checking logs, reading code across systems, testing deployments manually.
>
> That's the power of MCP tools in Claude Code."

**Final frame:**
- Text: "FastAPI MCP + Vercel MCP + Multi-System Debugging"
- URL: newcode.com/videos
- "Next: Serena MCP - Saving 60% on LLM Costs"

---

## 📝 Production Notes

### Camera Setup:
- **Main screen:** Claude Code conversation (full screen)
- **Picture-in-picture:** Terminal, browser, Prisma Studio (as needed)
- **Annotations:** Arrow highlights, circled text for key moments

### Key Moments to Highlight:
1. **0:30** - Contradiction: Backend says success, frontend stuck
2. **2:45** - Discovery: Routes not deployed (AHA moment)
3. **4:00** - Secondary bug spotted (shows AI thoroughness)
4. **5:45** - Real-time success (satisfying resolution)

### Post-Production Edits:
- Speed up file reading sequences (2x speed)
- Add split-screen for verification section
- Text overlays for Claude's key insights
- Background music: subtle, tech-focused

### B-Roll Footage (Optional):
- Vercel deployment dashboard
- Railway logs interface
- Prisma Studio interface
- Git commit history

---

## 🎓 Technical Concepts Explained

### For viewers unfamiliar with concepts:

**HTTP 405 Method Not Allowed:**
- Add text overlay: "405 = endpoint exists but doesn't support this HTTP method (GET/POST/PUT/DELETE)"

**Prisma:**
- Add text overlay: "Prisma = TypeScript database ORM (Object-Relational Mapping)"

**MCP (Model Context Protocol):**
- Add text overlay: "MCP = Tool protocol that lets AI agents access external services (Railway, Vercel, etc.)"

**Dynamic Routes in Next.js:**
- Add text overlay: "[runId] = dynamic route parameter (matches any value in URL)"

---

## 📊 Metrics to Show

**Debugging Speed:**
- Without Claude: 2-3 hours (manual log inspection, testing, debugging)
- With Claude: 7 minutes (automated analysis, cross-system investigation)

**Systems Investigated:**
- Backend: Python FastAPI (Railway)
- Frontend: TypeScript Next.js API (Vercel)
- Database: PostgreSQL (Prisma)
- Deployment: Vercel + Railway

**Bugs Found:**
- Primary: 405 errors (deployment mismatch)
- Secondary: Brand ID field name (data loading failure)

---

## 🔗 Related Resources

**Link in Description:**
- Error analysis document: [link to this repo file]
- Prisma integration guide: `backend/PRISMA_INTEGRATION.md`
- Next.js dynamic routes: https://nextjs.org/docs/app/building-your-application/routing/dynamic-routes
- Vercel deployment docs: https://vercel.com/docs/deployments

**GitHub Repo:**
- https://github.com/philbeliveau/innovation-intelligence-system
- Branch: `fix/prisma-405-errors-video`
- Commit: "docs: add video documentation for 405 error debugging"

**Newcode Resources:**
- MCP tools overview: newcode.com/mcp-tools
- FastAPI debugging guide: newcode.com/fastapi-debugging
- Multi-system debugging methodology: newcode.com/methodologies

---

## ✅ Pre-Flight Checklist

Before recording:
- [ ] Railway backend deployed and running
- [ ] Vercel frontend deployed (with OLD code missing routes)
- [ ] Test document ready to upload
- [ ] Railway logs accessible (showing 405 errors)
- [ ] Prisma Studio running (`npx prisma studio`)
- [ ] Claude Code MCP tools configured
- [ ] Screen recording software configured (1080p minimum)
- [ ] Audio tested (clear mic, no background noise)
- [ ] Backup: Second recording device (phone camera on screen)

---

**Last Updated:** 2025-10-25
**Status:** ✅ Ready for production
**Estimated Recording Time:** 15-20 minutes (edit to 5-7 minutes)

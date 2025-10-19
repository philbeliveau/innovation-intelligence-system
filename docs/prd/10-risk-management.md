# 10. Risk Management

## 10.1 Technical Risks

**Risk 1: Vercel Timeout (300s limit)**
- **Likelihood:** Medium
- **Impact:** High (pipeline takes 15-30 minutes)
- **Mitigation:** Use background execution with `exec()` (not `execSync()`)
- **Contingency:** Switch to cron + queue if background execution blocked

**Risk 2: Stage 1 Parsing Failure**
- **Likelihood:** Medium
- **Impact:** Medium (UI shows error instead of inspirations)
- **Mitigation:** Add fallback parsing with simpler regex
- **Contingency:** Display full markdown in single card instead of two-track

**Risk 3: Vercel Blob Upload Failure**
- **Likelihood:** Low
- **Impact:** High (no file = no pipeline)
- **Mitigation:** Add retry logic (3 attempts)
- **Contingency:** Save to local `/tmp` and skip Blob entirely

**Risk 4: Python Environment Issues on Vercel**
- **Likelihood:** Medium
- **Impact:** Critical (pipeline won't run)
- **Mitigation:** Test Python execution early in Phase 3
- **Contingency:** Run pipeline on separate server, use webhook to trigger

## 10.2 Scope Risks

**Risk 5: Feature Creep**
- **Likelihood:** High (temptation to add polish)
- **Impact:** High (miss hackathon deadline)
- **Mitigation:** Strictly follow 7-phase roadmap, skip all "nice-to-haves"

**Risk 6: UI Perfectionism**
- **Likelihood:** Medium
- **Impact:** Medium (time waste on styling)
- **Mitigation:** Use shadcn/ui MCP for instant components, no custom CSS

## 10.3 Timeline Risks

**Risk 7: Underestimated Phase Duration**
- **Likelihood:** High
- **Impact:** High (incomplete demo)
- **Mitigation:** Time-box each phase, move to next even if incomplete
- **Fallback Order:** Skip Phase 6 (Results) → Skip Phase 5 (Viewer polish) → Skip Phase 2 (Homepage polish)

---

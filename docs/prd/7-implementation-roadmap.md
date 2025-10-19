# 7. Implementation Roadmap

## 7.1 Phase Breakdown (1 Day = 8-10 hours)

**Phase 0.5: Onboarding/Landing Page at Root (1 hour)**
- Create `/app/page.tsx` as combined onboarding/landing page with "My Board of Ideators" design
- Implement colored circle layout (CSS Grid or absolute positioning)
- Add "My Board of Ideators" title with styled "My" in teal italics
- Create central text input for company name entry
- Add placeholder text: "Lactalis, Columbia, Decathlon, McCormick..."
- Implement company name validation and mapping logic
- On valid entry → call `/api/onboarding/set-company` → redirect to `/upload`
- Add error handling for invalid company names
- Add top navigation tabs (visual only, no functionality)
- Style matching `docs/image/Landing-page.png` reference
- **Note:** This is the root route (`/`), not a separate `/onboarding` route

**Phase 1: Setup (30 minutes)**
- Create Next.js app with TypeScript + Tailwind
- Install dependencies (`@vercel/blob`, `react-dropzone`, `react-markdown`)
- Set up shadcn/ui
- Add required components (`card`, `button`, `select`, `badge`, `skeleton`)
- Link existing pipeline directory

**Phase 2: Homepage UI (1.5 hours)**
- Use shadcn/ui MCP to generate upload component
- Create file upload zone with drag & drop
- Redirect to analyze page after upload
- Style to match `docs/image/main-page.png`

**Phase 3: Intermediary Card Page (1.5 hours)**
- Build `/analyze/[uploadId]/page.tsx`
- Display loading state during analysis
- Show card matching reference design
- Add "Launch" button

**Phase 4: API Routes (2 hours)**
- Build `/api/upload` with Vercel Blob integration
- Build `/api/analyze-document` with LLM extraction
- Build `/api/run` with Python subprocess execution
- Build `/api/status/[runId]` with log parsing
- Test API endpoints with Postman/curl

**Phase 5: Pipeline Modifications (1 hour)**
- Add `--input-file` and `--run-id` args to `run_pipeline.py`
- Implement `run_from_uploaded_file()` function
- Modify Stage 1 to output JSON with `_parse_inspirations()`
- Update Stage 1 prompt for structured output
- Test with CLI: `python run_pipeline.py --input-file test.pdf --brand lactalis-canada --run-id test-123`

**Phase 6: Pipeline Viewer UI (2.5 hours)**
- Create `/pipeline/[runId]/page.tsx`
- Build `InspirationTrack` component with skeleton loading
- Build `StageBox` component with status icons
- Implement status polling (5-second interval)
- Test with mock data

**Phase 6: Results Page (1 hour)**
- Create `/results/[runId]/page.tsx`
- Implement markdown file reading
- Render 5 opportunity cards with `react-markdown`
- Add "New Pipeline" and "Download PDF" buttons

**Phase 7: Deploy & Test (30 minutes)**
- Deploy to Vercel via CLI
- Set environment variables in Vercel dashboard
- Test end-to-end with `savannah-bananas.pdf` + Lactalis
- Fix any deployment issues

## 7.2 Success Checklist

- [ ] Root route (`/`) displays "My Board of Ideators" onboarding/landing page with circular design
- [ ] 8 colored circles arranged in circular pattern
- [ ] Central text input accepts company name (Lactalis, Columbia, Decathlon, McCormick)
- [ ] Company name validation works (case-insensitive)
- [ ] Valid company name loads brand profile and redirects to `/upload`
- [ ] Invalid company name shows error message
- [ ] Top navigation tabs visible (Everything, Spaces, Serendipity)
- [ ] No separate `/onboarding` route exists (all at root `/`)
- [ ] Company context saved to cookie and maintained throughout session
- [ ] Homepage displays upload zone matching reference design
- [ ] File upload to Vercel Blob works (< 5 seconds)
- [ ] Upload redirects to intermediary card page
- [ ] LLM analysis extracts title, summary, industry, theme, sources
- [ ] Intermediary card displays matching reference design
- [ ] "Launch" button triggers pipeline execution
- [ ] Pipeline viewer shows Stage 1 two-track UI
- [ ] Stage 1 inspirations load from JSON file
- [ ] Stages 2-5 show minimal status boxes
- [ ] Status polling updates UI every 5 seconds
- [ ] All 5 stages complete successfully
- [ ] Results page displays 5 opportunity cards
- [ ] Markdown rendering preserves formatting
- [ ] "New Pipeline" button returns to homepage
- [ ] Left sidebar shows "Home" button on hover
- [ ] App deployed to Vercel with public URL
- [ ] End-to-end test passes (upload → analyze → launch → process → results)

---

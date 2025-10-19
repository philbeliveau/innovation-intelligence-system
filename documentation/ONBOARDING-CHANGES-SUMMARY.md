# Onboarding Flow Changes Summary

**Date:** 2025-10-19
**Status:** Architecture & PRD Updated

---

## Overview

Updated the web app architecture to include a **team-led onboarding flow** where company context is pre-selected before homepage access. This enables clean client presentations without exposing multi-brand selector UI.

---

## Key Changes

### 1. New Onboarding Page (`/onboarding`)

**Purpose:** Team member selects target company before client demo

**Flow:**
1. Navigate to `/onboarding`
2. Select company from dropdown (Lactalis, McCormick, Columbia, Decathlon)
3. System loads brand profile from `/data/brand-profiles/{company-id}.yaml`
4. Company ID saved to HTTP-only cookie (7-day expiry)
5. Redirect to homepage with company context pre-loaded

**Implementation:**
- `app/onboarding/page.tsx` - Onboarding UI
- `app/api/onboarding/set-company/route.ts` - Loads YAML, sets cookie
- `app/api/onboarding/current-company/route.ts` - Reads current company from cookie

---

### 2. Updated Homepage (`/`)

**Changes:**
- ✅ **Company name displayed** at top-right corner (e.g., "Lactalis Canada 🏢")
- ❌ **No brand selector dropdown** (already set in onboarding)
- ✅ **Redirect to `/onboarding`** if no company cookie found
- ✅ **Cleaner UI** for client presentations

**API Changes:**
- `/api/run` now reads `brand_id` from cookie (not from request body)
- Returns 400 error if no company set → frontend redirects to onboarding

---

### 3. Brand Profile Integration

**Data Source:** `/data/brand-profiles/{company-id}.yaml`

**Files Available:**
- `lactalis-canada.yaml`
- `mccormick-usa.yaml`
- `columbia-sportswear.yaml`
- `decathlon.yaml`

**Data Loaded:**
```yaml
brand_name: Lactalis Canada
country: Canada
industry: Dairy / Food & Beverage
positioning: "Canada's premier dairy company..."
product_portfolio: [...]
target_customers: [...]
recent_innovations: [...]
strategic_priorities: [...]
brand_values: [...]
```

**Usage:**
- `brand_name` → Display on homepage
- `positioning`, `strategic_priorities`, `brand_values` → Used in pipeline Stages 4-5
- Cookie stores only `company_id`, full profile loaded on-demand

---

## Implementation Roadmap Updates

### New Phase: Hour 1-2 (Onboarding Page)

**Tasks:**
- [ ] Create `app/onboarding/page.tsx`
- [ ] Company selector dropdown (4 options)
- [ ] POST to `/api/onboarding/set-company` on selection
- [ ] Redirect to homepage with company context
- [ ] Create onboarding API routes
- [ ] Install `yaml` package for YAML parsing

**Dependencies:**
```bash
npm install yaml
```

### Updated Phase: Hour 2-4 (Homepage UI)

**Changes:**
- [ ] Display company name from cookie (top-right corner)
- [ ] ~~Add brand selector dropdown~~ (removed)
- [ ] Redirect to `/onboarding` if no company cookie found
- [ ] Update `/api/run` call to exclude `brand_id` from request

---

## API Specification Updates

### New: `POST /api/onboarding/set-company`

**Request:**
```json
{
  "company_id": "lactalis-canada"
}
```

**Response:**
```json
{
  "success": true,
  "company_id": "lactalis-canada",
  "company_name": "Lactalis Canada",
  "brand_profile": { ... }
}
```

**Side Effect:** Sets HTTP-only cookie `company_id` with 7-day expiry

---

### New: `GET /api/onboarding/current-company`

**Response:**
```json
{
  "company_id": "lactalis-canada",
  "company_name": "Lactalis Canada"
}
```

**Error (404):**
```json
{
  "error": "No company selected"
}
```

---

### Updated: `POST /api/run`

**Before:**
```json
{
  "blob_url": "https://...",
  "brand_id": "lactalis-canada"  // Passed in request
}
```

**After:**
```json
{
  "blob_url": "https://..."
  // brand_id read from cookie server-side
}
```

**Error Handling:**
- Returns 400 if no `company_id` cookie found
- Frontend redirects to `/onboarding` on 400 error

---

## User Flow Comparison

### Before (Brand Selector on Homepage)

```
Homepage
  ↓
Upload PDF
  ↓
Select Brand (Dropdown)  ← Client sees all brands
  ↓
Generate Opportunities
```

**Problem:** Exposes multi-brand selector during client presentations

---

### After (Onboarding Flow)

```
Onboarding (Team-Led)
  ↓
Select Company (Team Member)
  ↓
Homepage
  ↓
Upload PDF  ← Client only sees their brand name
  ↓
Generate Opportunities (No brand selection)
```

**Benefit:** Clean, single-brand presentation for clients

---

## Files Updated

### Architecture Document
**File:** `docs/architecture.md`

**Sections Modified:**
- Introduction (Purpose)
- System Diagram (added Onboarding node)
- User Journey (added Step 0: Onboarding)
- API Design (added onboarding endpoints)
- Implementation Roadmap (added Hour 1-2: Onboarding)

---

### PRD Document
**File:** `docs/prd.md`

**Sections Modified:**
- Executive Summary (added Key Change note)
- System Architecture diagram
- Core User Flow (added Onboarding step)
- Feature Requirements (added Section 4.0: Onboarding Page)
- Homepage Requirements (removed brand selector, added company display)
- Technical Specifications (updated API integration code)

---

## Next Steps

1. ✅ Architecture & PRD updated
2. ⏳ Implement onboarding page during Hour 1-2
3. ⏳ Update homepage to read company from cookie
4. ⏳ Test full flow: Onboarding → Upload → Pipeline → Results

---

## Benefits

### For Team
- Control which company context is active
- Clean setup before client demos
- No confusion with multi-brand selector

### For Clients
- See only their brand name
- Cleaner, more focused UI
- Professional presentation

### For Development
- Centralized brand profile management
- Reusable YAML data structure
- Session-based state (no database needed)

---

**Last Updated:** 2025-10-19
**Status:** Ready for implementation

# 1. Introduction

## Purpose

Build a **minimal web interface** that wraps the existing Python pipeline, enabling users to:
1. **Pre-select company** during team-led onboarding (loads brand context from YAML profiles)
2. Upload PDF trend reports via drag & drop
3. Watch real-time pipeline execution across 5 stages
4. View extracted trends, insights, and opportunity cards

**Key Change:** Brand selection happens during onboarding (before homepage), not on the homepage itself. This enables clean client presentations without exposing multi-brand selector.

## Core Philosophy

**Reuse, Don't Rebuild**
- Keep 100% of existing Python pipeline logic
- Add thin Next.js web layer on top
- Focus on UI/UX, not backend refactoring
- Ship in 1 day

## Key Constraints

- ⏱️ **8-10 hour build time** (hackathon scope)
- 🎨 **Ultra-minimal UI** (shadcn/ui components only)
- 🚫 **No database** (file-based state)
- 🚫 **No complex orchestration** (sequential API calls)
- ✅ **Vercel Blob for file storage**
- ✅ **Real-time stage visualization**

---

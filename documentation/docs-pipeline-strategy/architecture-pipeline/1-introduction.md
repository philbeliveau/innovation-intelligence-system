# 1. Introduction

## 1.1 Purpose

This architecture defines a **simple CLI-based Python tool** for validating the Innovation Intelligence Pipeline hypothesis. This is a **throwaway demo** designed for rapid validation (1-2 week build target), not a production system.

**Core Question:** Can an automated pipeline systematically transform market signals into brand-specific, actionable innovation opportunities worth $149-$1,500/month?

## 1.2 Scope

**In Scope:**
- Local Python CLI tool (`run_pipeline.py`)
- 5-stage LangChain pipeline (Input → Signal → Translation → Context → Opportunities)
- File-based storage (no database)
- Single test and batch execution modes
- Manual quality review with checklists
- 100 opportunity card generation (20 tests × 5 opportunities)

**Out of Scope:**
- Web UI or frontend
- Database or cloud storage
- Deployment infrastructure
- Real-time monitoring dashboards
- Automated quality scoring
- Production-grade error handling

## 1.3 Design Philosophy

> **"Make it work, then make it better"** - Focus on proving the transformation works, not building perfect software.

- **Simplicity over sophistication** - Hardcoded configurations acceptable
- **Local-first** - Everything runs on developer's machine
- **File-based** - All state persisted to filesystem
- **Manual intervention OK** - If a stage fails, manual retry is acceptable for 20 tests
- **Copy-paste patterns** - Use LangChain cookbook examples directly

---

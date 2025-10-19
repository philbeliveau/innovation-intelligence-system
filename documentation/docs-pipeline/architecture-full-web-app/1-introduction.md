# 1. Introduction

## Purpose

The **Innovation Intelligence Pipeline Testing System** is an experimentation platform designed to enable rapid iteration on a 5-stage LangChain-based pipeline that transforms market signals into brand-specific innovation opportunities. This architecture supports the core workflow defined in the PRD:

**Input** → **Signal Amplification** → **General Translation** → **Brand Contextualization** → **Opportunity Generation**

## Key Business Requirements

1. **Experimentation Platform**: Users need to test different prompts, models, and configurations to find optimal pipeline performance
2. **Cost Transparency**: LLM API calls are expensive - every test run must display estimated and actual costs
3. **Research Data Integration**: Each test requires comprehensive brand research data (120+ data points across 8 dimensions)
4. **One-at-a-Time Execution**: Run single tests with specific input/brand combinations for focused iteration
5. **Side-by-Side Comparison**: Compare opportunity outputs across different brands for the same input

## Architecture Decisions

**Platform Choice: Vercel**
- **Rationale**: Unified deployment for Next.js frontend + Python serverless functions, eliminates multi-cloud complexity
- **Constraints**: 300-second function timeout requires stage-by-stage execution (not monolithic pipeline)
- **Benefits**: Atomic deployments, instant rollbacks, integrated Blob storage and Postgres

**Storage Strategy: Hybrid (Postgres + Blob)**
- **Postgres**: Metadata, test run status, prompt configurations (fast queries, relational data)
- **Vercel Blob**: Raw inputs, research files, stage outputs, opportunity cards (large documents, versioning)
- **Rationale**: Postgres for indexing/search, Blob for cost-effective content storage

**UI Framework: Next.js 14 App Router + shadcn/ui**
- **Rationale**: React Server Components reduce client-side bundle, shadcn provides copy-paste components (no NPM bloat)
- **Monaco Editor**: VS Code-powered prompt editing with syntax highlighting and multi-line support

**LLM Access: OpenRouter API**
- **Rationale**: Single API for 6 models (DeepSeek to Claude Sonnet 4), no vendor lock-in, transparent pricing
- **Cost Range**: $0.14/1M tokens (DeepSeek) to $3.00/1M tokens (Claude Sonnet 4)

---

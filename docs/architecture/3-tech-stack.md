# 3. Tech Stack

## Complete Technology Matrix

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Frontend Framework** | Next.js | 15.1.8 | React Server Components + App Router |
| **UI Components** | shadcn/ui | latest | Minimal, accessible components |
| **UI Builder** | shadcn/ui MCP | latest | AI-powered component generation |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS |
| **State Management** | React useState | built-in | Local component state |
| **File Upload** | react-dropzone | 14.3+ | Drag & drop PDF upload |
| **Markdown Rendering** | react-markdown | 9.0+ | Display opportunity cards |
| **PDF Parsing** | pdf-parse | 1.1.1 | Extract text from PDFs |
| **YAML Parser** | yaml | 2.3.4 | Load brand profiles |
| **API Client** | Native fetch | built-in | Server/client data fetching |
| **Backend Framework** | FastAPI | 0.115.0 | Python REST API server (Railway) |
| **Backend Server** | uvicorn | 0.32.0 | ASGI server for FastAPI |
| **Backend Runtime** | Python | 3.11 | Pipeline execution environment |
| **Pipeline Framework** | LangChain | 0.1.0 | LLM orchestration |
| **LLM Provider** | OpenRouter | latest | Claude Sonnet 4.5 via API |
| **File Storage** | Vercel Blob | 0.23+ | PDF storage with public URLs |
| **Frontend Deployment** | Vercel | latest | Next.js hosting (serverless) |
| **Backend Deployment** | Railway | latest | FastAPI + Python pipeline hosting |
| **Containerization** | Docker | latest | Backend container image |
| **Environment** | Node.js | 20+ | Frontend API routes runtime |

## Why This Stack?

**Frontend (Vercel):**
- ✅ **Next.js 15**: React Server Components reduce client bundle size
- ✅ **shadcn/ui MCP**: Generate components via MCP tool (`mcp__magic__21st_magic_component_builder`)
- ✅ **Vercel Blob**: Simple API for file storage without S3 complexity
- ✅ **React Dropzone**: Proven drag & drop library

**Backend (Railway):**
- ✅ **FastAPI**: Modern Python web framework with automatic OpenAPI docs
- ✅ **Railway**: Simple deployment with Docker support, no serverless timeout issues
- ✅ **Existing Python Pipeline**: Zero refactoring of core pipeline logic
- ✅ **Independent Scaling**: Backend can scale independently from frontend

**Architecture Benefits:**
- ✅ **No Database**: File-based state for MVP simplicity
- ✅ **Separation of Concerns**: Frontend (Vercel) handles UI, Backend (Railway) handles processing
- ✅ **No Vercel Timeout**: Python pipeline runs on Railway without 300s serverless limit
- ✅ **Cost Effective**: ~$5/month Railway + free Vercel tier

---

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
| **Backend Runtime** | Python | 3.11 | Existing pipeline (unchanged) |
| **Pipeline Framework** | LangChain | 0.1.0 | Existing implementation |
| **LLM Provider** | OpenRouter | latest | Claude Sonnet 4.5 via existing setup |
| **File Storage** | Vercel Blob | 0.23+ | PDF storage with public URLs |
| **Deployment** | Vercel | latest | One-click deploy |
| **Environment** | Node.js | 20+ | API routes runtime |

## Why This Stack?

- ✅ **Next.js 15**: React Server Components reduce client bundle size
- ✅ **shadcn/ui MCP**: Generate components via MCP tool (`mcp__magic__21st_magic_component_builder`)
- ✅ **Vercel Blob**: Simple API for file storage without S3 complexity
- ✅ **No Database**: Avoid Postgres/Drizzle setup overhead
- ✅ **React Dropzone**: Proven drag & drop library
- ✅ **Existing Python Pipeline**: Zero refactoring needed

---

# 8. Deployment

## 8.1 Vercel Configuration

**`vercel.json`:**
```json
{
  "buildCommand": "npm run build",
  "framework": "nextjs",
  "env": {
    "OPENROUTER_API_KEY": "@openrouter-api-key",
    "OPENROUTER_BASE_URL": "https://openrouter.ai/api/v1",
    "LLM_MODEL": "deepseek/deepseek-chat",
    "BLOB_READ_WRITE_TOKEN": "@blob-read-write-token"
  },
  "functions": {
    "app/api/run/route.ts": {
      "maxDuration": 300
    }
  }
}
```

## 8.2 Environment Variables

**Required in Vercel Dashboard:**
- `OPENROUTER_API_KEY` - OpenRouter API key
- `BLOB_READ_WRITE_TOKEN` - Vercel Blob token (auto-generated)
- `LLM_MODEL` - Model identifier (default: `deepseek/deepseek-chat`)

## 8.3 Python Dependencies

**`requirements.txt`** (existing file, versions specified):
```
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.1
openai>=1.0.0
pypdf>=3.17.0
pyyaml>=6.0
jinja2>=3.1.3
python-dotenv>=1.0.0
pydantic>=2.5.0
```

## 8.4 Node.js Dependencies

**`package.json`** (create in innovation-web/ directory):
```json
{
  "name": "innovation-web",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@vercel/blob": "^0.23.0",
    "next": "15.1.8",
    "pdf-parse": "^1.1.1",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-dropzone": "^14.3.0",
    "react-markdown": "^9.0.0",
    "yaml": "^2.3.4"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.49",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.0.0"
  }
}
```

---

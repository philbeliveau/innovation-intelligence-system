# 10. Deployment Architecture

## Vercel Configuration

**File**: `vercel.json`

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "framework": "nextjs",
  "regions": ["iad1"],
  "functions": {
    "api/python/**/*.py": {
      "runtime": "python3.11",
      "maxDuration": 300,
      "memory": 1024
    }
  },
  "env": {
    "OPENROUTER_API_KEY": "@openrouter-api-key",
    "BLOB_READ_WRITE_TOKEN": "@blob-read-write-token",
    "POSTGRES_URL": "@postgres-url"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_APP_URL": "https://pipeline.yourdomain.com"
    }
  }
}
```

## Environment Variables

```bash
# Required for all environments (Development, Preview, Production)

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Vercel Blob Storage
BLOB_READ_WRITE_TOKEN=vercel_blob_rw_xxxxx

# Vercel Postgres
POSTGRES_URL=postgres://default:xxxxx@xxxxx-pooler.us-east-1.postgres.vercel-storage.com/verceldb
POSTGRES_PRISMA_URL=postgres://default:xxxxx@xxxxx-pooler.us-east-1.postgres.vercel-storage.com/verceldb?pgbouncer=true&connect_timeout=15
POSTGRES_URL_NON_POOLING=postgres://default:xxxxx@xxxxx.us-east-1.postgres.vercel-storage.com/verceldb

# Application URL (for OpenRouter HTTP-Referer header)
NEXT_PUBLIC_APP_URL=https://pipeline.yourdomain.com

# Monitoring (optional)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
AXIOM_TOKEN=xxxxx
```

## Python Requirements

**File**: `api/python/requirements.txt`

```txt
# LangChain ecosystem
langchain==0.1.0
langchain-openai==0.0.5
langchain-core==0.1.10

# OpenAI SDK (required by langchain-openai)
openai==1.10.0

# Vercel integrations
vercel-blob==0.2.0

# Templating and validation
jinja2==3.1.3
pydantic==2.5.3

# Utilities
requests==2.31.0
```

## CI/CD Pipeline

**File**: `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/coverage-final.json

  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pip install -r api/python/requirements.txt
      - run: pip install pytest pytest-cov pytest-asyncio
      - run: pytest api/python/tests --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - run: npm ci
      - run: npx playwright install --with-deps

      - run: npm run build
      - run: npm run test:e2e
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY_TEST }}
          BLOB_READ_WRITE_TOKEN: ${{ secrets.BLOB_TOKEN_TEST }}
          POSTGRES_URL: ${{ secrets.POSTGRES_URL_TEST }}

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

---

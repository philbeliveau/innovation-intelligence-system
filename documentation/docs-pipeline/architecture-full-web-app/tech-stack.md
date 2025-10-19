# 3. Tech Stack

## Complete Technology Matrix

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Frontend Framework** | Next.js | 15.1.8 | React Server Components + App Router |
| **UI Components** | shadcn/ui | latest | Copy-paste components, no NPM bloat |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS framework |
| **Code Editor** | Monaco Editor | 4.6.0 | VS Code-powered prompt editing |
| **React Wrapper** | @monaco-editor/react | 4.6.0 | React integration for Monaco |
| **State Management** | Zustand | 4.5+ | Lightweight client-side state |
| **Form Handling** | React Hook Form | 7.50+ | Type-safe form validation |
| **API Client** | Native Fetch | - | Built-in fetch with TypeScript types |
| **Backend Runtime** | Python | 3.11 | Vercel serverless functions |
| **LLM Framework** | LangChain | 0.1.0 | Pipeline orchestration |
| **LLM Integration** | langchain-openai | 0.0.5 | OpenRouter API compatibility |
| **LLM Provider** | OpenRouter | latest | Unified API gateway for 6+ models |
| **LLM Models** | Multiple providers | - | DeepSeek ($0.14/1M) to Claude Sonnet 4 ($3.00/1M) |
| **Database** | Vercel Postgres | latest | Metadata, configs, run status |
| **ORM** | Drizzle ORM | 0.30+ | Type-safe SQL queries |
| **Blob Storage** | Vercel Blob | 0.2.0 | Documents, outputs, research files |
| **Templating** | Jinja2 | 3.1.3 | Opportunity card generation |
| **Validation** | Pydantic | 2.5.3 | Python data validation |
| **Deployment** | Vercel | latest | Frontend + serverless deployment |
| **Monitoring** | Sentry | latest | Error tracking |
| **Logging** | Axiom | latest | Structured log aggregation |
| **Analytics** | Vercel Analytics | latest | Web vitals, user analytics |
| **Performance** | Vercel Speed Insights | latest | Real user monitoring |

## Model Configuration

```typescript
interface LLMModelConfiguration {
  id: string;
  provider: "deepseek" | "anthropic" | "openai" | "moonshot";
  display_name: string;
  model_identifier: string; // OpenRouter format: "provider/model-name"
  input_price_per_1m_tokens: number;
  output_price_per_1m_tokens: number;
  context_window: number;
  capabilities: string[];
  recommended_for: string;
}

const AVAILABLE_MODELS: LLMModelConfiguration[] = [
  {
    id: "deepseek-chat",
    provider: "deepseek",
    display_name: "DeepSeek Chat",
    model_identifier: "deepseek/deepseek-chat",
    input_price_per_1m_tokens: 0.14,
    output_price_per_1m_tokens: 0.28,
    context_window: 64000,
    capabilities: ["text"],
    recommended_for: "Cost-effective experimentation, high-volume testing",
  },
  {
    id: "claude-haiku-3-5",
    provider: "anthropic",
    display_name: "Claude Haiku 3.5",
    model_identifier: "anthropic/claude-3-5-haiku-20241022",
    input_price_per_1m_tokens: 0.80,
    output_price_per_1m_tokens: 4.00,
    context_window: 200000,
    capabilities: ["text"],
    recommended_for: "Fast processing, moderate quality requirements",
  },
  {
    id: "claude-sonnet-4",
    provider: "anthropic",
    display_name: "Claude Sonnet 4",
    model_identifier: "anthropic/claude-sonnet-4-20250514",
    input_price_per_1m_tokens: 3.00,
    output_price_per_1m_tokens: 15.00,
    context_window: 200000,
    capabilities: ["text", "vision"],
    recommended_for: "Highest quality outputs, critical stages (Stage 4)",
  },
  {
    id: "gpt-4o-mini",
    provider: "openai",
    display_name: "GPT-4o Mini",
    model_identifier: "openai/gpt-4o-mini",
    input_price_per_1m_tokens: 0.15,
    output_price_per_1m_tokens: 0.60,
    context_window: 128000,
    capabilities: ["text", "vision"],
    recommended_for: "Balanced cost and performance",
  },
  {
    id: "gpt-4o",
    provider: "openai",
    display_name: "GPT-4o",
    model_identifier: "openai/gpt-4o",
    input_price_per_1m_tokens: 2.50,
    output_price_per_1m_tokens: 10.00,
    context_window: 128000,
    capabilities: ["text", "vision"],
    recommended_for: "Complex reasoning, multi-modal inputs",
  },
  {
    id: "kimi-k1-5",
    provider: "moonshot",
    display_name: "Kimi K1.5",
    model_identifier: "moonshot/kimi-k1.5",
    input_price_per_1m_tokens: 0.30,
    output_price_per_1m_tokens: 0.30,
    context_window: 128000,
    capabilities: ["text"],
    recommended_for: "Long context processing, research synthesis",
  },
];
```

---

# 3. Architecture Principles

## 3.1 Core Principles

1. **Sequential Execution** - Stages run in order, each using previous outputs as input
2. **Stateless Stages** - Each stage is independent, no shared state beyond I/O
3. **File-Based Persistence** - All intermediate outputs saved to disk for debugging
4. **Fail-Fast** - Fatal errors halt execution immediately with clear error messages
5. **Context Preservation** - LangChain memory maintains context across stages

## 3.2 Simplicity Constraints

- **No Database** - All data in YAML/JSON/Markdown files
- **No API Server** - Direct Python script execution only
- **No Async** - Synchronous execution sufficient for 20 tests
- **No Complex Error Recovery** - Log error and halt, manual investigation acceptable
- **No Optimization** - Prioritize readability over performance

---

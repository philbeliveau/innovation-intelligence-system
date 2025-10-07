# 4. Technology Stack

## 4.1 Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Runtime** | Python | 3.10+ | Primary language |
| **LLM Framework** | LangChain | 0.1.0+ | Pipeline orchestration |
| **LLM Integration** | langchain-openai | 0.0.5+ | OpenRouter API client |
| **LLM Provider** | OpenRouter | latest | Unified API gateway |
| **LLM Model** | Claude Sonnet 4.5 | anthropic/claude-sonnet-4.5-20250514 | Primary reasoning model |
| **PDF Parsing** | pypdf | latest | Document ingestion |
| **Data Loading** | PyYAML | 6.0+ | Brand profile parsing |
| **Templating** | Jinja2 | 3.1+ | Opportunity card generation |
| **Validation** | Pydantic | 2.5+ | Data validation (optional) |

## 4.2 Python Dependencies

```txt
# requirements.txt
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

## 4.3 Development Tools

- **Virtual Environment:** `venv` (Python standard library)
- **Package Manager:** `pip`
- **Version Control:** Git
- **Code Formatting:** Black (optional)
- **Linting:** Flake8 (optional)

---

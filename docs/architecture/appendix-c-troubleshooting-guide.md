# Appendix C: Troubleshooting Guide

## C.1 Common Issues

**Problem:** `ModuleNotFoundError: No module named 'langchain'`
```bash
# Solution: Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Problem:** `OpenRouter API authentication failed`
```bash
# Solution: Verify API key in .env file
cat .env | grep OPENROUTER_API_KEY
# Test API key manually:
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE"
```

**Problem:** Stage output is empty or truncated
```bash
# Solution: Check LLM max_tokens setting, increase if needed
# Edit pipeline/stages/stageX_*.py and increase max_tokens parameter
```

**Problem:** `FileNotFoundError` when loading brand profile
```bash
# Solution: Verify brand ID matches filename (without .yaml)
ls data/brand-profiles/
# Correct: python run_pipeline.py --brand lactalis-canada
# Wrong: python run_pipeline.py --brand lactalis-canada.yaml
```

**Problem:** Pipeline hangs on Stage 4
```bash
# Solution: Check research data loading, may be reading large files
# Add verbose logging:
python run_pipeline.py --input X --brand Y --verbose
# Check logs/pipeline.log for details
```

---

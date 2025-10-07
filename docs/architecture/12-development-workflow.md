# 12. Development Workflow

## 12.1 Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd innovation-intelligence-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.template .env
# Edit .env and add your OPENROUTER_API_KEY

# 5. Verify setup
python -c "import langchain; from langchain_openai import ChatOpenAI; print('Environment ready')"

# 6. Run initial test
python run_pipeline.py --input savannah-bananas --brand lactalis-canada
```

## 12.2 Iterative Development Workflow

**Stage Development Cycle:**
1. **Implement stage** - Create stage module in `pipeline/stages/`
2. **Write prompt** - Define PromptTemplate in `pipeline/prompts/`
3. **Unit test** - Create test in `tests/` and verify stage works in isolation
4. **Integration test** - Run stage in full pipeline context
5. **Manual review** - Check output quality against rubric
6. **Prompt refinement** - Iterate on prompt based on quality review
7. **Re-test** - Verify improvements, commit when satisfied

**Example Stage Development:**
```bash
# Step 1: Implement Stage 1
vim pipeline/stages/stage1_input_processing.py
vim pipeline/prompts/stage1_prompt.py

# Step 2: Unit test
python -m pytest tests/test_stage1.py -v

# Step 3: Integration test
python tests/test_stages_1_3.py

# Step 4: Manual quality review
cat data/test-outputs/savannah-bananas-lactalis-*/stage1/inspiration-analysis.md
# Review against docs/stage-1-3-quality-checklist.md

# Step 5: Refine prompt if needed
vim pipeline/prompts/stage1_prompt.py

# Step 6: Re-test
python run_pipeline.py --input savannah-bananas --brand lactalis-canada

# Step 7: Commit when satisfied
git add pipeline/stages/stage1_input_processing.py pipeline/prompts/stage1_prompt.py
git commit -m "Implement Stage 1: Input Processing"
```

## 12.3 Validation Testing Workflow

**After Epic 4 (all stages implemented):**

```bash
# 1. Run full batch test
python run_pipeline.py --batch

# 2. Review batch summary
cat data/test-outputs/batch-summary.md

# 3. Sample 20 opportunities for quality review
python scripts/sample_opportunities.py --count 20 --output quality-assessment.csv

# 4. Manual scoring
# Fill out quality-assessment.csv with scores (1-5 for each dimension)

# 5. Analyze results
python scripts/analyze_quality.py --input quality-assessment.csv

# 6. Document findings
vim docs/validation-results.md

# 7. Make recommendation (proceed/pivot/iterate)
```

## 12.4 Prompt Engineering Best Practices

1. **Start simple** - Get basic functionality working before optimizing
2. **Use examples** - Include 1-2 examples in prompts for clarity
3. **Be specific** - Exact output format requirements prevent parsing errors
4. **Test edge cases** - Try shortest/longest inputs, different document types
5. **Version prompts** - Git commit after each prompt refinement
6. **Document rationale** - Comment why specific prompt instructions were added

---

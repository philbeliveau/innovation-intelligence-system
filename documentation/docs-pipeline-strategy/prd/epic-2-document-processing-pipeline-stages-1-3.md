# Epic 2: Document Processing Pipeline (Stages 1-3)

**Expanded Goal:** Implement the three offline document analysis stages that transform raw PDF/markdown inputs into brand-agnostic universal insights. Each stage is a LangChain LLMChain with specific prompting strategy. Epic delivers a functional pipeline that can process any input document and generate high-quality universal lessons without external dependencies.

## Story 2.1: Stage 1 - Input Processing and Inspiration Identification

As a **pipeline developer**,
I want **Stage 1 implemented as a LangChain LLMChain that reviews input documents and identifies key inspiration elements**,
so that **the pipeline can extract the most relevant insights from diverse input types**.

### Acceptance Criteria

1. File created: `pipeline/stages/stage1_input_processing.py` with `Stage1Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage1_prompt.py` with instructions:
   - Review input document thoroughly
   - Identify 3-5 key inspiration elements (innovations, strategies, successful tactics)
   - For each inspiration, note: what it is, why it's interesting, potential applicability
   - Summarize overall context and significance
3. Stage 1 chain uses ChatOpenAI configured for OpenRouter (Claude Sonnet 4.5 via anthropic/claude-sonnet-4.5) with temperature=0.3 for consistency
4. Output format: Structured markdown with sections: "Document Overview", "Key Inspirations" (numbered list), "Context Notes"
5. Stage 1 integrated into `run_pipeline.py` with output saved to `stage1/inspiration-analysis.md`
6. Test execution: Run on Savannah Bananas input, verify output contains 3-5 inspirations with descriptions
7. Stage output passes through to Stage 2 successfully

## Story 2.2: Stage 2 - Trend Extraction from Document Content

As a **pipeline developer**,
I want **Stage 2 implemented to extract trend patterns from document content without external social media data**,
so that **the pipeline can amplify signals using only the information present in input documents**.

### Acceptance Criteria

1. File created: `pipeline/stages/stage2_signal_amplification.py` with `Stage2Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage2_prompt.py` with methodology:
   - Analyze Stage 1 inspirations for recurring themes and patterns
   - Identify underlying trends: consumer behavior shifts, industry movements, emerging needs
   - Extract relevant broader context (industry trends mentioned in document)
   - Categorize trends by: behavioral, technological, cultural, economic
3. Trend extraction methodology documented in `docs/stage2-trend-methodology.md` explaining pattern recognition approach
4. Stage 2 chain receives Stage 1 output as input variable
5. Output format: Structured markdown with sections: "Identified Trends" (bulleted with categories), "Signal Strength Assessment" (high/medium/low per trend), "Trend Context"
6. Stage 2 integrated into `run_pipeline.py` with output saved to `stage2/trend-analysis.md`
7. Test execution: Run on Savannah Bananas → Stage 1 → Stage 2, verify trends extracted without requiring external data
8. Manual review confirms trends are derived from document content, not LLM general knowledge

## Story 2.3: Stage 3 - General Translation to Universal Lessons

As a **pipeline developer**,
I want **Stage 3 implemented to translate inspirations and trends into brand-agnostic universal principles**,
so that **Stage 4 can apply these principles to any brand context**.

### Acceptance Criteria

1. File created: `pipeline/stages/stage3_general_translation.py` with `Stage3Chain` class
2. LangChain PromptTemplate defined in `pipeline/prompts/stage3_prompt.py` with instructions:
   - Synthesize Stage 1 inspirations + Stage 2 trends into universal lessons
   - De-contextualize: remove specific brand/industry references, extract underlying principles
   - Generate 5-7 universal lessons applicable across industries
   - For each lesson: principle statement + why it works + where it could apply
3. Optional: Integration with innovation frameworks from `documentation/document/` (TRIZ, SIT, biomimicry) - reference frameworks in prompt if helpful
4. Stage 3 chain receives Stage 1 + Stage 2 outputs as concatenated input
5. Output format: Structured markdown with section "Universal Lessons" (numbered list with sub-bullets for explanation and applicability)
6. Stage 3 integrated into `run_pipeline.py` with output saved to `stage3/universal-lessons.md`
7. Test execution: Run full pipeline Stages 1-3 on Savannah Bananas, verify lessons are brand-agnostic (no mention of baseball or specific brand)
8. Quality check: Manual review confirms lessons are actionable and truly universal (could apply to CPG, retail, services, etc.)

## Story 2.4: Stages 1-3 Integration Testing and Refinement

As a **pipeline developer**,
I want **integration testing across all 3 document processing stages with prompt refinement**,
so that **the offline pipeline produces high-quality universal insights consistently**.

### Acceptance Criteria

1. Integration test script created: `test_stages_1_3.py` that runs full Stage 1-3 pipeline on all 5 inputs
2. Test execution generates 5 sets of outputs (one per input) in `data/test-outputs/integration-test-stages-1-3/`
3. Quality checklist created for manual review (`docs/stage-1-3-quality-checklist.md`):
   - Stage 1: Are inspirations specific and actionable?
   - Stage 2: Are trends derived from document (not hallucinated)?
   - Stage 3: Are lessons truly universal (de-contextualized)?
4. Manual quality review completed on all 5 outputs using checklist
5. Prompt refinements implemented based on quality review findings
6. Re-run integration test after prompt refinement, verify quality improvements
7. Documentation updated: Each stage's PromptTemplate documented with rationale for key instructions
8. Success metric: 4 out of 5 inputs produce "good quality" outputs (pass quality checklist)

---

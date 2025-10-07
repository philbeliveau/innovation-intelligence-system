# Documentation Index

## Pipeline Documentation

### Quick Start
- **[Pipeline Quick Reference](pipeline-quick-reference.md)** - One-page cheat sheet with commands, file locations, and key numbers
- **[Pipeline Documentation](pipeline-documentation.md)** - Complete technical documentation covering all 5 stages, data flow, testing, and configuration
- **[Pipeline Flow Diagram](../pipeline-flow-diagram.md)** - Visual Mermaid diagram (paste into mermaid.live)

### Core Specifications
- **[Opportunity Card Format](opportunity-card-format.md)** - Template and structure for generated opportunity cards
- **[Brand Research Data Structure](brand-research-data-structure.md)** - Format for brand research data used in Stage 4
- **[Model Configuration](model-configuration.md)** - LLM configuration, temperature settings, and API details

---

## User Stories

### Epic 1: Foundation & Data Setup
- [Story 1.1](stories/story-1.1-documentation-assets-organization.md) - Documentation & Assets Organization
- [Story 1.2](stories/story-1.2-test-input-documents.md) - Test Input Documents
- [Story 1.3](stories/story-1.3-brand-research-data.md) - Brand Research Data Collection
- [Story 1.4](stories/story-1.4-output-structure-definition.md) - Output Structure Definition
- [Story 1.5](stories/story-1.5-pipeline-scaffolding.md) - Pipeline Scaffolding

### Epic 2: Stages 1-3 Development
- [Story 2.1](stories/story-2.1-stage1-input-processing.md) - Stage 1: Input Processing
- [Story 2.2](stories/story-2.2-stage2-signal-amplification.md) - Stage 2: Signal Amplification
- [Story 2.3](stories/story-2.3-stage3-general-translation.md) - Stage 3: General Translation
- [Story 2.4](stories/story-2.4-stages-1-3-integration-testing.md) - Stages 1-3 Integration Testing ✅ COMPLETE

### Epic 3: Stages 4 Development
- [Story 3.1](stories/story-3.1-research-data-integration.md) - Research Data Integration
- [Story 3.2](stories/story-3.2-stage4-brand-contextualization.md) - Stage 4: Brand Contextualization

### Epic 4: Stage 5 & Complete Testing
- [Story 4.1](stories/story-4.1-opportunity-card-format-template.md) - Opportunity Card Format & Template
- [Story 4.2](stories/story-4.2-stage5-opportunity-generation.md) - Stage 5: Opportunity Generation ✅ COMPLETE
- [Story 4.3](stories/story-4.3-complete-batch-execution.md) - Complete Batch Execution (24 scenarios)
- [Story 4.4](stories/story-4.4-quality-assessment-validation.md) - Quality Assessment & Validation
- [Story 4.5](stories/story-4.5-documentation-handoff.md) - Documentation & Handoff

---

## QA Gates

Quality assurance checkpoints for each story:

- [Gate 2.4](qa/gates/2.4-stages-1-3-integration-testing.yml) - Stages 1-3 Integration Testing
- [Gate 3.1](qa/gates/3.1-research-data-integration.yml) - Research Data Integration
- [Gate 3.2](qa/gates/3.2-stage4-brand-contextualization.yml) - Stage 4 Brand Contextualization
- [Gate 4.1](qa/gates/4.1-opportunity-card-format-template.yml) - Opportunity Card Format
- [Gate 4.2](qa/gates/4.2-stage5-opportunity-generation.yml) - Stage 5 Opportunity Generation

---

## Examples

Sample outputs demonstrating pipeline quality:

### Stage Outputs
- [Stage 1 Example](examples/stage1-savannah-bananas-example.md) - Inspiration analysis
- [Stage 2 Example](examples/stage2-savannah-bananas-example.md) - Signal amplification
- [Stage 3 Example](examples/stage3-savannah-bananas-example.md) - Universal lessons

### Opportunity Cards
- [Product Innovation Example](examples/opportunity-product-example.md)
- [Service Innovation Example](examples/opportunity-service-example.md)
- [Marketing Innovation Example](examples/opportunity-marketing-example.md)
- [Experience Innovation Example](examples/opportunity-experience-example.md)
- [Partnership Innovation Example](examples/opportunity-partnership-example.md)

---

## Architecture & Research

### Project Context
- **[CLAUDE.md](../CLAUDE.md)** - Project overview, business context, working principles, BMAD integration

### Research Foundation
Located in `/bmad-adaptation/research/`:
- Psychological and cognitive science foundations (9 documents)
- Innovation methodologies (TRIZ, SIT, Lateral Thinking, Biomimicry)
- Latest neuroscience and creativity research

### Agent Personas
Located in `/bmad-adaptation/agent-personas/`:
- 7 specialized psychological profiles
- Big Five personality traits
- Unique capabilities and interaction protocols

### Workflow Design
Located in `/bmad-adaptation/workflows/`:
- Complete end-to-end system workflow
- Phase-by-phase processing pipeline
- Intelligence generation and validation stages

---

## Testing

### Test Files
- `test_stages_1_3.py` - Integration test for Stages 1-3 (6 inputs)
- `test_stage4.py` - Integration test for Stage 4 (TBD)
- `test_stages_1_4_integration.py` - Full pipeline test Stages 1-4 (TBD)
- `test_stage5_opportunity_generation.py` - Unit tests for Stage 5 (TBD - REQUIRED)

### Test Data
- **Inputs:** 6 PDF documents in `documentation/document/`
- **Brand Research:** 4 brand directories in `data/brand-research/`
- **Test Scenarios:** 24 total (6 inputs × 4 brands)

### Test Coverage Status
- ✅ Story 2.1 (Stage 1): Unit tests complete
- ✅ Story 2.4 (Stages 1-3): Integration tests complete
- ✅ Story 4.1 (Template): 16 comprehensive tests complete
- ⚠️ Story 4.2 (Stage 5): **Zero automated tests** (manual verification only)

---

## Quick Navigation

### I want to...

**Understand the pipeline:**
→ Start with [Pipeline Quick Reference](pipeline-quick-reference.md)

**Run the pipeline:**
→ See commands in [Pipeline Documentation](pipeline-documentation.md#execution-modes)

**Review test results:**
→ Check `data/test-outputs/integration-test-stages-1-3/test-summary.md`

**See code structure:**
→ View [Pipeline Documentation - File Structure](pipeline-documentation.md#file-structure)

**Understand opportunity cards:**
→ Read [Opportunity Card Format](opportunity-card-format.md)

**Check quality standards:**
→ Review [QA Gates](qa/gates/)

**Visualize the flow:**
→ Open [Pipeline Flow Diagram](../pipeline-flow-diagram.md) in mermaid.live

**Add brand research:**
→ Follow [Brand Research Data Structure](brand-research-data-structure.md)

---

## Key Metrics

| Metric | Current Value |
|--------|---------------|
| **Total Scenarios** | 24 (6 inputs × 4 brands) |
| **Completed Stories** | 2 of 14 (14%) |
| **Pipeline Stages** | 5 |
| **Test Coverage** | Stages 1-3 ✅, Stage 4 ⚠️, Stage 5 ⚠️ |
| **Success Rate Target** | ≥95% (23/24) |
| **Execution Time (Batch)** | ~36-48 minutes |

---

## Current Status

### ✅ Complete
- Story 2.1: Stage 1 Input Processing
- Story 2.4: Stages 1-3 Integration Testing (6/6 tests passing)
- Story 4.1: Opportunity Card Template (16 tests)
- Story 4.2: Stage 5 Opportunity Generation (implementation complete, needs tests)

### 🚧 In Progress
- Story 4.3: Batch Execution (24 scenarios)

### ⏳ Planned
- Story 3.1: Research Data Integration
- Story 3.2: Stage 4 Brand Contextualization
- Story 4.4: Quality Assessment
- Story 4.5: Documentation Handoff

---

## Contributing

When adding documentation:

1. **User Stories:** Add to `/docs/stories/` following story template
2. **QA Gates:** Add to `/docs/qa/gates/` following YAML format
3. **Examples:** Add to `/docs/examples/` with clear naming
4. **Update this README** with new documentation links

---

**Documentation Version:** 1.0
**Last Updated:** 2025-10-07
**Maintained By:** Innovation Intelligence Pipeline Team

# 5. Pipeline Architecture

## 5.1 LangChain Components

```python
# Simplified Architecture Diagram (Python pseudocode)

from langchain.chains import LLMChain, SequentialChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Initialize LLM
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-sonnet-4.5-20250514",
    temperature=0.5
)

# Define 5 stage chains
stage1_chain = LLMChain(
    llm=llm,
    prompt=stage1_prompt_template,
    output_key="stage1_output"
)

stage2_chain = LLMChain(
    llm=llm,
    prompt=stage2_prompt_template,
    output_key="stage2_output"
)

# ... stage3, stage4, stage5 chains

# Connect into sequential pipeline
pipeline = SequentialChain(
    chains=[stage1_chain, stage2_chain, stage3_chain, stage4_chain, stage5_chain],
    input_variables=["input_document", "brand_profile", "research_data"],
    output_variables=["stage1_output", "stage2_output", "stage3_output",
                     "stage4_output", "stage5_output"],
    verbose=True
)

# Execute
results = pipeline({
    "input_document": loaded_pdf_content,
    "brand_profile": loaded_brand_yaml,
    "research_data": loaded_research_files
})
```

## 5.2 Stage Isolation

Each stage is implemented as a separate module in `pipeline/stages/`:

```
pipeline/stages/
├── stage1_input_processing.py      # Returns inspiration analysis
├── stage2_signal_amplification.py  # Returns trend analysis
├── stage3_general_translation.py   # Returns universal lessons
├── stage4_brand_contextualization.py # Returns brand insights
└── stage5_opportunity_generation.py  # Returns 5 opportunity cards
```

**Each stage module exports:**
- `create_chain(llm)` - Returns configured LLMChain
- `get_prompt_template()` - Returns PromptTemplate
- `save_output(output, directory)` - Persists stage output to file

---

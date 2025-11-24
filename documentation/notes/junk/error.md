 And I cant save the experiment: Error: Save failed:
  {"detail":[{"type":"string_type","loc":["body","run_id"],
  "msg":"Input should be a valid
  string","input":null},{"type":"string_type","loc":["body"
  ,"report_text"],"msg":"Input should be a valid
  string","input":null},{"type":"dict_type","loc":["body","
  brand_profile"],"msg":"Input should be a valid
  dictionary","input":null}]} 

   │ Root Cause Analysis                                   │ │
│ │                                                       │ │
│ │ The PDF is displaying raw JSON instead of formatted   │ │
│ │ markdown. Based on my investigation, I've identified  │ │
│ │ these potential issues in the data flow:              │ │
│ │                                                       │ │
│ │ Backend → Gradio → PDF Chain:                         │ │
│ │ 1. Backend generates stage_data["output"] (dict with  │ │
│ │ opportunities)                                        │ │
│ │ 2. Backend calls format_stage_output() to create      │ │
│ │ stage_data["markdown"] (formatted string)             │ │
│ │ 3. Gradio's get_stage_display() extracts              │ │
│ │ stage_data["markdown"]                                │ │
│ │ 4. Gradio stores it in                                │ │
│ │ state["stage_outputs"]["stage_5"]["markdown"]         │ │
│ │ 5. PDF generator extracts state.get("stage_outputs"). │ │
│ │ get("stage_5").get("markdown")                        │ │
│ │ 6. PDF generator passes it to markdown2.markdown()    │ │
│ │ for HTML conversion                                   │ │
│ │                                                       │ │
│ │ Identified Issues:                                    │ │
│ │                                                       │ │
│ │ 1. Backend formatting may be failing - If             │ │
│ │ format_stage_output() throws an exception,            │ │
│ │ stage_data["markdown"] never gets set, causing Gradio │ │
│ │  to fall back to raw JSON                             │ │
│ │ 2. Type confusion - The stage_data["output"] for      │ │
│ │ Stage 5 contains a nested structure with              │ │
│ │ opportunities array, which                            │ │
│ │ format_stage5_to_markdown() expects                   │ │
│ │ 3. PDF generator receiving dicts instead of strings - │ │
│ │  The truncated dict output suggests the markdown      │ │
│ │ field contains a string representation of a dict      │ │
│ │                                                       │ │
│ │ Fix Plan                                              │ │
│ │                                                       │ │
│ │ Step 1: Add defensive type checking to backend        │ │
│ │ format_stage_output()                                 │ │
│ │                                                       │ │
│ │ - File: backend/pipeline/output_formatters.py         │ │
│ │ - Change: Add better error handling and type          │ │
│ │ validation                                            │ │
│ │ - Why: Prevent silent failures that leave markdown    │ │
│ │ field unset                                           │ │
│ │                                                       │ │
│ │ Step 2: Fix format_stage5_to_markdown() to handle     │ │
│ │ potential type issues                                 │ │
│ │                                                       │ │
│ │ - File: backend/pipeline/output_formatters.py         │ │
│ │ - Change: Add validation that opp['markdown'] is      │ │
│ │ actually a string before appending                    │ │
│ │ - Why: Prevent dict objects from being treated as     │ │
│ │ strings                                               │ │
│ │                                                       │ │
│ │ Step 3: Add logging to track markdown field           │ │
│ │ generation                                            │ │
│ │                                                       │ │
│ │ - File: backend/app/pipeline_runner.py                │ │
│ │ - Change: Log the type and length of generated        │ │
│ │ markdown for each stage                               │ │
│ │ - Why: Help debug where the data type conversion is   │ │
│ │ failing                                               │ │
│ │                                                       │ │
│ │ Step 4: Verify Gradio get_stage_display() fallback is │ │
│ │  working correctly                                    │ │
│ │                                                       │ │
│ │ - File:                                               │ │
│ │ backend/experimentation/hf-space-deploy/app.py        │ │
│ │ - Change: Add type checking before returning markdown │ │
│ │  from get_stage_display()                             │ │
│ │ - Why: Ensure only strings are passed to PDF          │ │
│ │ generator                                             │ │
│ │                                                       │ │
│ │ Step 5: Test and deploy                               │ │
│ │                                                       │ │
│ │ - Push changes to Railway backend (for fixes #1-3)    │ │
│ │ - Push changes to HuggingFace Space (for fix #4)      │ │
│ │ - Test full pipeline → PDF download flow              │ │
│ │                                                       │ │
│ │ Expected Outcome: PDFs will display beautifully       │ │
│ │ formatted markdown with headings, bullet points, and  │ │
│ │ sections instead of raw JSON dicts.                   │ │
│ ╰──────────────────────────────────────────────


Now, explain me why when I save the an output run, and when I set the Quality Assessment to good, no examples actually saves.

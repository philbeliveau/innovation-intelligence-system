# Task: Create Video Documentation

**Purpose:** Automate the process of documenting bugs/features for Newcode video production

**Elicit:** true

**When to use:** When encountering a bug or implementing a feature that would make a good video demonstration

---

## Task Overview

This task automates the creation of comprehensive video documentation for the Newcode video series. It creates a dedicated branch, generates three core documents (error analysis, technical script, non-technical script), commits, and pushes to remote.

---

## Execution Steps

### Step 1: Elicit Video Context

**Ask the user:**

```
I'll help you create comprehensive video documentation for this scenario.

Please provide:

1. **What is the subject?** (Bug fix / Feature implementation / Debugging session / Other)

2. **Brief description:** (1-2 sentences about what happened)

3. **Target Newcode video subject:** (Which of the 20 video subjects does this match?)
   - Subject 1: FastAPI MCP Debugging
   - Subject 2: Serena MCP (Token optimization)
   - Subject 3: Vercel & Railway MCP (Deployment)
   - Subject 4: Playwright MCP (Testing)
   - Subject 5: Sub-agents
   - Subject 6: Loop & Verification
   - Subject 7: The Modern Stack
   - Subject 8: Prisma MCP
   - Subject 9: Context7 MCP
   - Subject 10: GitHub MCP
   - Subject 11: Clerk MCP
   - Subject 12: Stripe
   - Subject 13: Hero Demo
   - Subject 14: Custom Instructions
   - Subject 15: Memory & Context Management
   - Subject 16: Diagnostic Brownfield
   - Subject 17: TDD
   - Subject 18: Refactoring
   - Subject 19: Web Scraping
   - Subject 20: Multi-agent Swarms

4. **Error logs or key context?** (Paste relevant logs, error messages, or context)

5. **Files involved:** (List key files that were modified or investigated)

6. **Estimated video duration:** (3-4 min / 5-7 min / other)
```

---

### Step 2: Create Branch

**Branch naming convention:**
- For bugs: `fix/{feature-name}-video`
- For features: `feat/{feature-name}-video`
- For refactors: `refactor/{feature-name}-video`

**Commands:**
```bash
# Get current branch
git branch --show-current

# Create new branch with -video suffix
git checkout -b {branch-name}
```

---

### Step 3: Create Directory Structure

```bash
mkdir -p documentation/NEWCODE/video-plan
```

---

### Step 4: Generate Error Analysis Document

**File:** `documentation/NEWCODE/video-plan/error-analysis-{topic}.md`

**Template Structure:**
```markdown
# Error Analysis: {Topic}

**Date:** {current-date}
**Branch:** {current-branch}
**Error Type:** {error-classification}
**Impact:** {impact-level}
**Severity:** {severity-level}

---

## 🔴 Error Summary
{1-2 paragraph summary of the issue}

---

## 📊 Error Logs
{Relevant logs, formatted}

---

## 🏗️ Architecture Context
{Architecture diagrams, before/after states}

---

## 🔍 Root Cause Analysis
{Detailed investigation findings}

---

## 🧪 Diagnosis Steps
{Step-by-step diagnostic process}

---

## 🎯 Likely Root Causes
{Ranked list of probable causes}

---

## 🔧 Recommended Fix Sequence
{Ordered list of fixes to apply}

---

## ✅ Verification Tests
{How to verify the fix works}

---

## 📊 Success Criteria
{What "fixed" looks like}

---

## 📚 Related Documentation
{Links to related docs}

---

## 🎬 Video Documentation
{Link to companion video scripts}
```

---

### Step 5: Generate Technical Video Script

**File:** `documentation/NEWCODE/video-plan/video-scenario-technical.md`

**Template Structure:**
```markdown
# Video Scenario: Technical Version
## "{Video Title}"

**Video Series:** Newcode - Subject {N}: {Subject Name}
**Target Audience:** Developers, technical managers, DevOps engineers
**Duration:** {duration}
**Difficulty:** {level}

---

## 🎯 Learning Objectives
{Bullet points of what viewers will learn}

---

## 📋 Pre-Recording Setup
{Environment state, required access, test data}

---

## 🎬 Video Script

### [0:00-0:30] Hook - The Problem
{Script, screen recording notes, narration}

### [0:30-1:00] Initial Investigation
{Script, screen recording notes, narration}

### [1:00-2:00] Discovery
{Script, screen recording notes, narration}

### [2:00-3:00] The Fix
{Script, screen recording notes, narration}

### [3:00-4:00] Verification
{Script, screen recording notes, narration}

### [4:00-end] Takeaways
{Script, screen recording notes, narration}

---

## 📝 Production Notes
{Camera setup, key moments, post-production edits}

---

## 🎓 Technical Concepts Explained
{Definitions for complex terms}

---

## 📊 Metrics to Show
{Time savings, systems investigated, bugs found}

---

## 🔗 Related Resources
{Links in description, GitHub repo, related docs}

---

## ✅ Pre-Flight Checklist
{Items to verify before recording}
```

---

### Step 6: Generate Non-Technical Video Script

**File:** `documentation/NEWCODE/video-plan/video-scenario-non-technical.md`

**Template Structure:**
```markdown
# Video Scenario: Non-Technical Version
## "{Simplified Title}"

**Video Series:** Newcode - Subject {N}: {Subject Name} (Simplified)
**Target Audience:** Business owners, managers, entrepreneurs, non-developers
**Duration:** 3-4 minutes
**Difficulty:** Beginner (no coding knowledge required)

---

## 🎯 Video Goals
{What non-technical viewers should understand}

---

## 📋 Pre-Recording Setup
{What to prepare, what to HIDE}

---

## 🎬 Video Script

### [0:00-0:30] Hook - The Problem
{Script using plain English, no jargon}

### [0:30-1:00] Ask AI for Help
{Show typing simple question}

### [1:00-2:00] Watch AI Work
{Visualize investigation, hide complexity}

### [2:00-3:00] The Fix
{One-click solutions, no code shown}

### [3:00-3:30] It Works!
{Happy resolution, time saved}

### [3:30-4:00] The Takeaway
{Key lessons in simple terms}

---

## 🎨 Visual Style Guide
{Colors, typography, animations, icons}

---

## 🎙️ Narration Style
{Tone, language rules, emphasis points}

---

## 📊 Metrics to Highlight
{Time/cost savings, complexity hidden}

---

## 🎬 Production Checklist
{Pre-recording, during, post-production}

---

## 🎯 Success Metrics
{Engagement goals, viral potential}

---

## 💡 Alternative Hooks
{Test different opening angles}

---

## 🔗 Video Description Template
{YouTube/LinkedIn description copy}
```

---

### Step 7: Commit and Push

**Commit message template:**
```bash
git add documentation/NEWCODE/video-plan/

git commit -m "$(cat <<'EOF'
docs(video): add {topic} video documentation

Create video plan for Newcode Subject {N}: {Subject Name}

Added three comprehensive documents:

1. error-analysis-{topic}.md
   - {Brief description}

2. video-scenario-technical.md
   - {Duration} technical video script
   - Target: Developers, DevOps
   - {Key demonstration points}

3. video-scenario-non-technical.md
   - 3-4 minute simplified script
   - Target: Business owners, non-developers
   - {Key messaging points}

Context:
- {Project context}
- {Showcase value}

Related to: {related-files}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push origin {branch-name}
```

---

### Step 8: Return to Original Branch

```bash
git checkout {original-branch}
```

---

### Step 9: Provide Summary

**Output to user:**
```
✅ Video documentation created successfully!

Branch: {branch-name}
Files created:
  - documentation/NEWCODE/video-plan/error-analysis-{topic}.md
  - documentation/NEWCODE/video-plan/video-scenario-technical.md
  - documentation/NEWCODE/video-plan/video-scenario-non-technical.md

GitHub: https://github.com/{user}/{repo}/tree/{branch-name}

Next steps:
1. Review the documentation for accuracy
2. Schedule video recording session
3. Prepare test environment per pre-flight checklist
4. Record technical version (5-7 min)
5. Record non-technical version (3-4 min)
6. Edit and publish

The documentation branch is ready for pull request if needed.
```

---

## Quality Checks

Before completing task, verify:

- [ ] Branch created with `-video` suffix
- [ ] All 3 documents created in correct directory
- [ ] Error analysis includes logs and root cause
- [ ] Technical script has timestamped sections
- [ ] Non-technical script avoids jargon
- [ ] Commit message follows template
- [ ] Branch pushed to remote successfully
- [ ] User returned to original branch
- [ ] Summary provided with next steps

---

## Error Handling

**If branch creation fails:**
- Check if branch already exists
- Suggest alternative branch name

**If commit fails:**
- Verify files were created
- Check git status
- Provide debugging suggestions

**If push fails:**
- Check remote connection
- Verify branch name
- Suggest manual push command

---

## Example Usage

**User input:**
```
Subject: FastAPI debugging
Description: Pipeline completes but database never updates, 405 errors
Video subject: Subject 1 - FastAPI MCP
Logs: [pasted Railway logs]
Files: backend/app/prisma_client.py, innovation-web/app/api/pipeline/[runId]/stage-update/route.ts
Duration: 5-7 min
```

**Agent output:**
- Creates `fix/prisma-405-errors-video` branch
- Generates 3 comprehensive documents
- Commits with detailed message
- Pushes to GitHub
- Returns to original branch
- Provides summary with next steps

---

## Integration with BMAD

This task can be called via:
```
/BMad:agents:dev *create-video-documentation
```

Or from any agent when encountering a video-worthy scenario:
```
*create-video-documentation
```

---

**Last Updated:** 2025-10-25
**Author:** Claude Code
**Status:** ✅ Ready for use

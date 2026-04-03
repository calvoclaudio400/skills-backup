---
name: workspace-token-optimizer
description: Audit and optimize OpenClaw workspace token overhead, memory structure, and model routing. Use when user asks to reduce workspace token costs or optimize injected context.
metadata:
  openclaw:
    emoji: 🧠
---

# Workspace Token Optimizer

## Description
Automatically audit and optimize your OpenClaw workspace for token efficiency. Scans boot files, memory structure, skill loading, and model routing — then applies fixes.

## Trigger
- "Optimize my workspace tokens"
- "Audit my token usage"
- "How much am I wasting on tokens?"
- "Reduce my API costs"

## Workflow

### Phase 1: Workspace Audit
1. Scan all files loaded at boot (IDENTITY.md, SOUL.md, MEMORY.md, AGENTS.md, skills/).
2. Count total tokens injected per session start.
3. Identify files over 100 lines (flag for compression).
4. Check MEMORY.md — should be a routing index under 50 lines, not a knowledge dump.
5. Check for duplicate content across boot files.

### Phase 2: Model Routing Analysis
1. Review current model assignments (which tasks use Opus vs Sonnet vs Haiku).
2. Flag tasks using Opus that could use Sonnet (simple edits, formatting, file operations).
3. Flag tasks using Sonnet that could use Haiku (classification, routing, yes/no decisions).
4. Calculate estimated monthly savings from model downgrades.

### Phase 3: Skill Loading Optimization
1. Count skills in skills/ directory.
2. Identify skills loaded but never triggered in recent sessions.
3. Recommend lazy-loading patterns for infrequently used skills.
4. Check skill file sizes — flag any over 200 lines for splitting.

### Phase 4: Memory Architecture Review
1. Verify MEMORY.md follows routing-index pattern (links to topic files, not inline content).
2. Check for stale memory files (not updated in 7+ days).
3. Identify memory files over 100 lines that should be archived or compressed.
4. Ensure session state is separate from durable knowledge.

### Phase 5: Apply Fixes
1. Present optimization report with estimated savings.
2. For each recommendation, show before/after token counts.
3. Apply approved changes:
   - Compress verbose boot files.
   - Move inline knowledge to referenced files.
   - Update model routing suggestions in AGENTS.md.
   - Archive stale memory files.
4. Re-audit and confirm new token baseline.

## Output Format
```
=== Workspace Token Audit ===
Boot tokens:     [X] tokens ([Y] files loaded)
Memory tokens:   [X] tokens ([Y] files)
Skill tokens:    [X] tokens ([Y] skills loaded)
Total per session: [X] tokens

Optimization opportunities:
1. [File] — [current tokens] → [target tokens] (save [N]%)
2. [Model routing] — [task] uses [current] → suggest [cheaper]
3. [Memory] — [file] is [N] lines, compress to [M]

Estimated monthly savings: $[X] (from $[current] to $[optimized])
```

## Guardrails
- Never delete files without confirmation.
- Always show before/after comparison before applying changes.
- Preserve all information — compress, don't discard.
- Back up files before modifying (copy to .bak).

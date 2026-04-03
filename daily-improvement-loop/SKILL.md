---
name: daily-improvement-loop
description: Run daily self-improvement loops for assistant speed, quality, and reliability. Use when optimizing task throughput, reducing response latency, tightening execution flow, reviewing bottlenecks, or planning daily incremental upgrades.
---

# Daily Improvement Loop

## Core loop (run daily)
1. Measure baseline from latest logs and active sessions:
   - first-ack latency
   - median task completion time
   - queue depth by chat
   - fallback/error rate (5xx, timeout, auth)
2. Identify top 3 bottlenecks by impact.
3. Apply only high-signal changes that improve speed without breaking safety.
4. Verify with before/after metrics.
5. Persist continuity:
   - update `memory/YYYY-MM-DD.md`
   - if durable, distill to `MEMORY.md`
   - commit and push immediately.

## Fast execution policy
- Acknowledge quickly when work may exceed ~5 seconds.
- Parallelize independent units; serialize only true dependencies.
- Batch file operations and status updates.
- Use fallback early on repeated failures.

## Improvement targets
- First acknowledgment: <= 2s
- Typical simple task completion: <= 15s
- Tool error retry path: <= 8s failover
- Queue growth: controlled (no unbounded pending)

## Safety boundaries
- Never skip confirmations for destructive/public actions.
- Never store raw secrets in memory/docs unless explicitly instructed.
- HARD RULE: any downloaded skill code (even from ClawHub/ShopClawMart) must be scanned for malicious patterns / security flaws BEFORE install. Never install blind — verify first.

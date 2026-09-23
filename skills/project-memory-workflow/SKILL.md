---
name: "Project Memory Workflow"
description: "Use when the user wants a persistent project memory for a repo, wants Codex to keep a living memory document updated after changes, or asks to create repo-local rules that force memory maintenance as part of every task."
---

# Project Memory Workflow

Use this skill to turn project context into a maintained repo artifact instead of leaving it in transient chat history.

## Goal

Set up a reusable workflow inside any repository so that:

- the repo has a durable memory file
- the memory reflects current code, not only old discussion
- future tasks update that memory as part of Definition of Done

## Default outputs

Unless the repo already has an established convention, use:

- `AGENTS.md` in the repo root for repo-local rules
- `docs/project-memory.md` for the living memory document

If the repo already uses a different convention, merge into that convention instead of duplicating it.

## Setup workflow

1. Inspect the repo before writing anything.
   - Find current entrypoints, architecture, important modules, state/storage patterns, networking setup, build system, and any existing repo instructions.
   - Check whether `AGENTS.md`, `memory.md`, `docs/`, or similar documentation already exists.

2. Create or update repo-local rules.
   - Add a short `AGENTS.md` rule set that makes memory maintenance mandatory.
   - Require reading the memory file before non-trivial work.
   - Require updating the memory file after every change.
   - Keep the rule file short; the detailed knowledge belongs in the memory file.

3. Create or update the memory file.
   - Put durable repo knowledge in `docs/project-memory.md`.
   - Seed it from the current codebase first.
   - If local thread history is available and relevant, incorporate only repo-scoped, high-signal decisions.

4. Make the memory file living, not static.
   - It must work as both a current-state reference and a lightweight change log.
   - When a new change supersedes an old one, update the old statement instead of letting contradictions accumulate.

## Memory file structure

Use this default structure unless the repo needs a different one:

- `تعريف المشروع`
- `الحالة الحالية`
- `المعمارية والملفات المحورية`
- `قرارات ثابتة`
- `سجل التغييرات`
- `Open Questions / نقاط تحتاج متابعة`

If the user prefers English, use the same structure in English.

For a starter template, see `references/memory-template.md`.

## What belongs in project memory

Include:

- project purpose and product context that affects implementation
- actual current flows and behaviors
- architecture and important file locations
- durable engineering decisions
- historical decisions only when they still matter or were superseded later
- naming/product terminology changes that affect code or UX

Do not include:

- transient build logs
- machine-specific noise
- unrelated repo work
- low-signal line-by-line changelog text
- speculative statements that are not grounded in repo facts

## Update rules for future tasks

After any task in that repo:

- small change: add one compact entry under `سجل التغييرات`
- larger behavioral or architectural change: update `الحالة الحالية` or `قرارات ثابتة`, then add a log entry
- replaced decision: edit the old note so the file stays internally consistent

The memory file should stay concise. Compress trivial changes instead of letting the file sprawl.

## Source priority

Prefer sources in this order:

1. current repo code
2. repo-local instructions and docs
3. relevant local thread history tied to the same repo
4. explicit user clarifications

If thread history conflicts with current code, document the old change as historical and keep current code as source of truth.

## Output expectations

When using this skill, the implementation should usually result in:

- a repo-root `AGENTS.md` or equivalent update
- a `docs/project-memory.md` or equivalent memory file
- an initial seeded memory snapshot
- future tasks updating that memory automatically as part of completion

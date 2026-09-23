# clean-code-guard

Review generated or changed production code before it ships, using Clean Code, SOLID, DRY, KISS, YAGNI, and LLM-specific failure-mode checks in any programming language. Best used reactively after an agent writes, edits, refactors, or fixes code, before presenting, committing, or merging the result. Use when the user asks "review this PR", "is this safe to merge?", "make this cleaner", "audit this code", "refactor this", "fix this bug", or after a coding agent produced implementation code. Can also guide writing when explicitly invoked before a risky edit. Invoke it on your own initiative the moment you finish writing, editing, or refactoring non-trivial production code, before presenting or committing — don't wait to be asked. DO NOT USE for factual/conceptual questions, CI/tooling config, git workflow, running/debugging tests, pure architecture discussion, prose writing, data analysis, or test-code review (use test-guard).

## Activation

Use this skill when the request matches the trigger and scope described in `SKILL.md`.

## Prerequisites

Read `SKILL.md` before use. Any tool, runtime, connector, or project requirements are documented there.

## Contents

- `SKILL.md`
- `agents/`
- `references/`

## Usage

Copy this directory into your Codex skills directory, then invoke the skill by its name when the request matches its scope. `SKILL.md` is the authoritative specification.

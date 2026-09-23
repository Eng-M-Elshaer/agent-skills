# test-guard

Review generated or changed test code against universal testing rules before it ships. Best used reactively after an agent writes, edits, generates, or refactors tests, before presenting, committing, or merging them. Use for pytest (test_*.py, *_test.py), PHPUnit/Pest (*Test.php), Jest/Vitest (*.test.ts, *.spec.js), Go (*_test.go), files under tests/, __tests__/, or spec/, and review requests like 'write tests for X', 'add tests', 'test this', 'review these tests', or PR diffs containing tests. Can also guide test writing when explicitly invoked before the work. This skill is the quality gate that prevents AI-generated test bloat. DO NOT USE for production or implementation code review (use clean-code-guard), CI or test-runner configuration, running or debugging tests, or general architecture discussion.

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

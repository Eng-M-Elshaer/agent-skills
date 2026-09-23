# docs-guard

Review generated or changed documentation before it ships — READMEs, API references, docstrings, PHPDoc/JSDoc, changelogs, tutorials, and doc sites. Best used reactively after an agent writes or edits docs, after code changes documented behavior, or before publishing docs. Use when the user says 'review the docs', 'is this documentation accurate', 'update the docs', 'write a README', 'document this API', 'add a docstring', or 'add a changelog entry'. Core job: verify every referenced function, flag, endpoint, config key, and code sample against the source; catch docs-vs-code drift; strip filler and unverifiable claims. DO NOT USE for production code review (use clean-code-guard), test review (use test-guard), marketing copy or blog posts, prose style editing of non-technical writing, or documentation site theming.

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

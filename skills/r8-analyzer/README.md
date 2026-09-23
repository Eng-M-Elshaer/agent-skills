# r8-analyzer

Analyzes Android build files and R8 keep rules to identify redundancies, broad package-wide rules, and rules that subsume library consumer keep rules. Use when developers want to optimize their app's size, remove redundant or overly broad keep rules, or troubleshoot Proguard configurations.

## Activation

Use this skill when the request matches the trigger and scope described in `SKILL.md`.

## Prerequisites

Read `SKILL.md` before use. Any tool, runtime, connector, or project requirements are documented there.

## Contents

- `SKILL.md`
- `references/`

## Usage

Copy this directory into your Codex skills directory, then invoke the skill by its name when the request matches its scope. `SKILL.md` is the authoritative specification.

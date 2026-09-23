<skill>
<name>project-orchestrator</name>
<path>/Users/restart/.codex/skills/project-orchestrator/SKILL.md</path>
---
name: project-orchestrator
description: Orchestrate architecture, style, and rules skills
metadata:
  short-description: Orchestrate architecture, style, and rules skills
---

# Project Orchestrator Skill

This master skill coordinates the Architecture Reader, Style Detector, and Rules Enforcer skills. It ensures that Codex understands the project context and applies all relevant rules before generating or modifying code.

## How It Works

1. **Initialization**: When entering a new project, run the *Architecture Reader Skill* to analyze the directory structure, identify the architecture pattern, build a dependency graph, and produce a high‑level summary of the project. Save this summary in memory for future reference.
2. **Style Extraction**: Next, run the *Style Detector Skill* to infer naming conventions, folder organization, state management patterns, dependency injection method, and other stylistic details. Produce a style profile describing how classes, variables, files, directories, and routes are named and organized. Store this profile in memory.
3. **Rule Compilation**: Load the *Rules Enforcer Skill*. Combine the project's architecture and style information with the general project rules contained in `skill_rules.md`. This produces a complete set of constraints for the project. The rules may include project‑specific instructions (e.g., “use Cubit for state management,” “use `freezed` for models,” “use `go_router` for navigation,” etc.) and general constraints from the Flutter documentation.
4. **Ongoing Enforcement**:
   - **Code generation**: When Codex generates new code, it must check against the compiled rules. Names, files, folders, and class structures should follow the style profile. Data access must flow through repositories and services as defined by the architecture summary. All code must satisfy the rules listed in `skill_rules.md`.
   - **Code modification**: When modifying existing code, verify that the changes preserve the architecture (view → view model → repository → service) and do not introduce logic into the UI layer. If the modification violates any rule, adjust the design or recommend a refactoring.
   - **New features**: For new features, create a new feature folder following the existing structure (e.g., `features/new_feature/ui/`, `features/new_feature/state/`, `features/new_feature/data/`). Implement view models, repositories, and services according to the architecture pattern and naming conventions. Register dependencies in the DI container and define new routes in the navigation system.
5. **Memory and updates**: After any significant changes, update the architecture summary and style profile to reflect the new state of the project. This ensures that subsequent changes continue to follow the latest conventions.

## Usage

- Run this master skill immediately after cloning or opening a project. It will populate the architecture and style context and set up the rules for Codex to follow.
- Before each new coding session, re‑run the architecture and style skills if there have been significant changes to the project structure.
- Consult the compiled rules whenever making decisions about folder structure, file names, state management, data access, navigation, or formatting.
- If a new team member or tool needs to understand the project, provide them with the architecture summary, style profile, and rules files to ensure consistent contributions.

By orchestrating the other skills, this master skill ensures that Codex maintains a deep understanding of the project and consistently produces code that matches the established architecture and style while complying with all project rules.
</skill>

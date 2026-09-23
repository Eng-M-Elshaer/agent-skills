---
name: my-project-rules
description: Create or update repo-local project rules for a new or existing project. Use when setting up a project for the user's default workflow, creating or refreshing AGENTS.md, enforcing persistent project memory, selecting relevant skills automatically by project type, or onboarding Codex into a repository before implementation work.
---

# My Project Rules

Use this skill to install the user's default repo rules into a project. The primary output is a root `AGENTS.md` section that future Codex sessions read automatically, plus a starter `docs/project-memory.md` when no project memory exists.

## Workflow

1. Confirm the project root.
   - Default to the current working directory.
   - If the user names a path, use that path.
   - Inspect the repo before writing: list top-level files and detect project type from files such as `pubspec.yaml`, `Package.swift`, `*.xcodeproj`, `build.gradle`, `settings.gradle`, `firebase.json`, or `package.json`.

2. Run the setup script from the project root:

```bash
python3 /Users/restart/.codex/skills/my-project-rules/scripts/setup_project_rules.py --root .
```

3. Review the resulting files.
   - `AGENTS.md` must contain the user's default workflow rules.
   - `docs/project-memory.md` must exist unless the repo already uses another memory convention.
   - Preserve unrelated existing `AGENTS.md` content.

4. After setup, apply the rules immediately for the rest of the task.

## Installed Rules

The generated `AGENTS.md` tells future agents to:

- Use `Project Memory Workflow` for persistent repo memory.
- Read `AGENTS.md` and `docs/project-memory.md` before every non-trivial task.
- Record decisions, fixes, ideas, problems, and rules in project memory using the sections `قرار`, `اصلاح`, `فكرة`, `مشكلة`, and `قواعد`.
- Update memory after every task so it stays current.
- Use `divide-and-conquer` before complex or multi-step work.
- After understanding the task, review the available skills and use any skill that can help before implementation.
- Use `ponytail` for coding tasks to keep the solution minimal, native, and shortest-working-diff first.
- Use `clean-code-guard` on changed production code before presenting, committing, or merging it.
- Use `caveman` for terse, high-signal responses unless clarity requires normal mode.
- Follow SOLID in production code and UI architecture.
- Keep a project architecture record in `ARC.md`; if a new project has no arc yet, ask the user which architecture to follow before implementation.
- Extract the code style from existing projects into `Style.md`; if a new project has no style yet, ask the user what style to follow before implementation.
- Choose Firebase skills automatically for Firebase work without asking.
- Gather discoverable information directly instead of asking the user.
- Use `screenshot` for UI changes when a visual check is available.
- Follow commit prefixes: `[Add]`, `[Modify]`, or `[Fix]`.
- Mention the skills used at the end of each task.
- Execute the task with Luna 5.6 at Medium reasoning/effort.
- At the end of the task, perform the review with a Sol 5.6 Medium sub-agent selected according to the project's language and framework before presenting the result.
- Act as a senior specialist for the project type before implementation:
  - iOS: act as a Senior iOS Developer.
  - Android: act as a Senior Android Developer.
  - Flutter: act as a Senior Flutter Developer.
  - Use the most relevant skills for that stack before coding.
  - If the backend is Firebase, use the matching Firebase skills before coding.

## Skill Selection Rules

Apply these when the generated rules are active:

- Coding tasks: use `ponytail` first, then apply `clean-code-guard` before delivery.
- Response style: use `caveman` for concise, high-signal wording unless the user needs clarity in normal mode.
- Architecture: follow SOLID and keep `ARC.md` as the project architecture record. For new projects, ask which architecture/arc to follow before first implementation.
- Style: extract the code style into `Style.md` for existing projects. For new projects, ask which style to follow before first implementation.
- Flutter: act as a Senior Flutter Developer, then use `flutter-laam-project-style` before implementation when the project follows Flutter, Clean Architecture, BLoC/Cubit, Freezed, Dio, or GetIt patterns. Use `flutter-architecture-reviewer` for architecture review or when structure decisions are involved if that skill is installed.
- iOS: act as a Senior iOS Developer, then search for and use relevant Swift, SwiftUI, iOS debugging, performance, and architecture skills before implementation.
- Android: act as a Senior Android Developer, then search for and use relevant Android, Kotlin, Jetpack Compose, Gradle, emulator QA, and architecture skills before implementation.
- Backend/Firebase: if the backend is Firebase, search for and use the matching Firebase skills before implementation.
- Firebase: use available Firebase skills automatically for authentication, Firestore, hosting, app hosting, Data Connect, AI Logic, and other Firebase tasks.
- UI changes: use the most specific visual verification tool available; use `screenshot` when OS-level or simulator screenshots are needed.
- UI components: before creating any UI view, widget, screen component, or visual element, evaluate whether it should be reusable and design it with SOLID principles where they apply.
- Model workflow: use Luna 5.6 at Medium for implementation, then use a Sol 5.6 Medium sub-agent specialized for the project's language/framework as the final reviewer.

## Script Behavior

`scripts/setup_project_rules.py`:

- Creates `AGENTS.md` if missing.
- Updates only the managed `My Project Rules` block if `AGENTS.md` already exists.
- Creates `docs/project-memory.md` with the required memory sections if missing.
- Does not overwrite existing project memory.
- Prints the changed file paths.

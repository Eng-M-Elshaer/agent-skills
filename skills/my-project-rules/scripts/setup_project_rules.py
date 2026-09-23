#!/usr/bin/env python3
"""Install the user's default project rules into a repository."""

from __future__ import annotations

import argparse
from pathlib import Path


BEGIN = "<!-- BEGIN MY PROJECT RULES -->"
END = "<!-- END MY PROJECT RULES -->"


RULES_BLOCK = f"""{BEGIN}
# My Project Rules

These rules are mandatory for every Codex task in this repository.

## Memory

- Use the `Project Memory Workflow` skill for persistent project memory.
- Read this `AGENTS.md` and `docs/project-memory.md` before every non-trivial task or request.
- Keep `docs/project-memory.md` current after every task.
- Record durable items under the matching memory section: `قرار`, `اصلاح`, `فكرة`, `مشكلة`, or `قواعد`.
- Update older memory entries when they are superseded instead of leaving contradictions.

## Task Workflow

- Use the `divide-and-conquer` skill before complex, ambiguous, or multi-step work.
- After understanding the task, review the available skills and use any skill that can help before implementation.
- Use `ponytail` for coding tasks to keep the solution minimal, native, and shortest-working-diff first.
- Before shipping changed or generated production code, run `clean-code-guard` on the diff and fix any rule breaks.
- For response style, use `caveman` for terse, high-signal wording unless clarity requires normal mode.
- Follow SOLID in production code and UI architecture.
- Keep a project architecture record in `ARC.md`; if a new project has no arc yet, ask the user which architecture to follow before implementation.
- Extract the code style from existing projects into `Style.md`; if a new project has no style yet, ask the user what style to follow before implementation.
- If the task is backend work and the project backend is Firebase, automatically use the relevant Firebase skills.
- If information can be discovered from the repo, tools, docs, or the web when appropriate, get it directly instead of asking the user.
- Use available Firebase skills automatically for Firebase tasks without asking first.
- At the end of each task, mention the skills used.

## UI Verification

- Before creating any UI view, widget, screen component, or visual element, evaluate whether it should be reusable.
- Apply SOLID principles before implementation where they fit UI architecture, especially single responsibility, dependency inversion, and open/closed extension points.
- For UI changes, use the best available visual verification tool.
- Use the `screenshot` skill for simulator, emulator, desktop, or OS-level screenshots when needed.
- If a commit includes UI changes, capture or reference a screenshot of the updated UI when feasible.

## Commits

- Use `[Add]` at the start of commit messages for additions.
- Use `[Modify]` at the start of commit messages for modifications.
- Use `[Fix]` at the start of commit messages for fixes.

## Project-Type Skills

- Flutter: act as a Senior Flutter Developer before implementation. Use `flutter-laam-project-style` when applicable. Use `flutter-architecture-reviewer` for architecture-sensitive work if installed. Search for and use other relevant Flutter skills before coding.
- iOS: act as a Senior iOS Developer before implementation. Search for and use relevant Swift, SwiftUI, iOS debugging, performance, and architecture skills before coding.
- Android: act as a Senior Android Developer before implementation. Search for and use relevant Android, Kotlin, Jetpack Compose, Gradle, emulator QA, and architecture skills before coding.
- Backend/Firebase: if the backend is Firebase, use the Firebase skills that match the task before coding.
{END}
"""


MEMORY_TEMPLATE = """# Project Memory

## تعريف المشروع

- اكتب هدف المشروع وسياق المنتج هنا بعد فحص الكود.

## الحالة الحالية

- اكتب الحالة الحالية للتطبيق أو النظام هنا.

## المعمارية والملفات المحورية

- اكتب أهم المسارات والطبقات ونقاط الدخول هنا.

## قرار

- سجل القرارات الهندسية أو المنتجية الثابتة هنا.

## اصلاح

- سجل الإصلاحات المهمة التي تؤثر على السلوك أو الجودة هنا.

## فكرة

- سجل الأفكار القابلة للتنفيذ أو التحسينات المقترحة هنا.

## مشكلة

- سجل المشاكل المعروفة أو المخاطر أو القيود هنا.

## قواعد

- سجل قواعد المشروع التي يجب استمرار الالتزام بها هنا.

## سجل التغييرات

- سجل ملخصًا موجزًا بعد كل مهمة.

## Open Questions / نقاط تحتاج متابعة

- سجل الأسئلة المفتوحة التي تحتاج قرارًا أو تحققًا لاحقًا.
"""


def update_managed_block(existing: str) -> str:
    if BEGIN in existing and END in existing:
        before = existing.split(BEGIN, 1)[0].rstrip()
        after = existing.split(END, 1)[1].lstrip()
        parts = [before, RULES_BLOCK.rstrip(), after.rstrip()]
        return "\n\n".join(part for part in parts if part) + "\n"

    if existing.strip():
        return existing.rstrip() + "\n\n" + RULES_BLOCK

    return RULES_BLOCK


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update AGENTS.md and project memory rules.")
    parser.add_argument("--root", default=".", help="Project root directory")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)

    changed: list[Path] = []

    agents_path = root / "AGENTS.md"
    existing_agents = agents_path.read_text(encoding="utf-8") if agents_path.exists() else ""
    new_agents = update_managed_block(existing_agents)
    if new_agents != existing_agents:
        agents_path.write_text(new_agents, encoding="utf-8")
        changed.append(agents_path)

    docs_dir = root / "docs"
    memory_path = docs_dir / "project-memory.md"
    if not memory_path.exists():
        docs_dir.mkdir(parents=True, exist_ok=True)
        memory_path.write_text(MEMORY_TEMPLATE, encoding="utf-8")
        changed.append(memory_path)

    if changed:
        print("Updated:")
        for path in changed:
            print(path)
    else:
        print("No changes needed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

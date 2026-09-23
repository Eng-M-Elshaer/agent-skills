#!/usr/bin/env python3
"""Generate concise README files for the copied Codex skills."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def frontmatter(text: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.*?)(?=^\w[^:]*:|\Z)", text, re.MULTILINE | re.DOTALL)
    if not match:
        return ""
    value = match.group(1).strip()
    if value in {">", "|", ">-", "|-"}:
        value = re.split(r"\n(?=\w[^ ]*:)", value)[0]
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"(^|\s)>\s*", r"\1", value)
    return value.strip().strip('"').strip("'")


def metadata(skill_dir: Path) -> tuple[str, str]:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^---\s*\n(.*?)^---\s*$", text, re.MULTILINE | re.DOTALL)
    block = match.group(1) if match else ""
    name = frontmatter(block, "name") or skill_dir.name
    description = frontmatter(block, "description") or "See SKILL.md for the authoritative instructions."
    return name, description


def entries(skill_dir: Path) -> list[str]:
    return sorted(
        p.name + ("/" if p.is_dir() else "")
        for p in skill_dir.iterdir()
        if p.name not in {"README.md"}
    )


def skill_readme(skill_dir: Path, name: str, description: str) -> str:
    listed = entries(skill_dir)
    contents = "\n".join(f"- `{item}`" for item in listed) or "- `SKILL.md`"
    return f"""# {name}\n\n{description}\n\n## Activation\n\nUse this skill when the request matches the trigger and scope described in `SKILL.md`.\n\n## Prerequisites\n\nRead `SKILL.md` before use. Any tool, runtime, connector, or project requirements are documented there.\n\n## Contents\n\n{contents}\n\n## Usage\n\nCopy this directory into your Codex skills directory, then invoke the skill by its name when the request matches its scope. `SKILL.md` is the authoritative specification.\n"""


def main() -> None:
    skill_rows: list[tuple[str, str, str]] = []
    for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name != ".system"):
        name, description = metadata(skill_dir)
        readme = skill_dir / "README.md"
        if not readme.exists() or skill_dir.name != "ios-27-scene-lifecycle-audit":
            readme.write_text(skill_readme(skill_dir, name, description), encoding="utf-8")
        skill_rows.append((skill_dir.name, name, description))

    rows = "\n".join(
        f"| [`{folder}`](skills/{folder}/README.md) | {name} | {description[:220].replace('|', '/')} |"
        for folder, name, description in skill_rows
    )
    root_readme = f"""# Agent Skills\n\nA collection of Codex skills copied from the local `~/.codex/skills` directory. Each skill keeps its complete source bundle, including `SKILL.md`, references, scripts, assets, tests, and any embedded license files.\n\n## Installation\n\nCopy the skill directories you need into your Codex skills directory:\n\n```sh\ncp -R skills/<skill-name> ~/.codex/skills/\n```\n\nRead each skill's `README.md` for a concise guide and its `SKILL.md` for the complete instructions.\n\n## Skills\n\n| Skill | Name | Description |\n| --- | --- | --- |\n{rows}\n"""
    (ROOT / "README.md").write_text(root_readme, encoding="utf-8")


if __name__ == "__main__":
    main()

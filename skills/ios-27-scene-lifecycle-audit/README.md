# iOS 27 Scene Lifecycle Audit Skill

A portable Agent Skill for auditing UIKit projects before or during migration to the iOS 27 SDK scene-lifecycle requirement.

## What it does

- Detects whether a UIKit project has usable `UIScene` configuration.
- Reviews `AppDelegate`, `SceneDelegate`, `Info.plist`, and storyboard/programmatic window ownership.
- Flags launch-time UI access from `didFinishLaunching`.
- Flags legacy AppDelegate lifecycle callbacks that stop being the correct UI lifecycle hook after scene adoption.
- Flags brittle `connectedScenes.first` and legacy `AppDelegate.window` usage.
- Reviews deep-link and push-notification routing risks.
- Produces a minimal safe remediation plan instead of rewriting the app.

## Codex install

For one repository, copy the whole folder to:

```text
<repo>/.agents/skills/ios-27-scene-lifecycle-audit/
```

For a global personal skill, copy it to:

```text
~/.agents/skills/ios-27-scene-lifecycle-audit/
```

Codex discovers skills from `SKILL.md`. Restart Codex if a newly added skill does not appear.

## Manual scanner

```bash
python3 scripts/audit_scene_lifecycle.py /path/to/ios/project
```

JSON:

```bash
python3 scripts/audit_scene_lifecycle.py /path/to/ios/project --json
```

The scanner is read-only.

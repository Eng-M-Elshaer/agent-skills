#!/usr/bin/env python3
"""
Read-only static audit for UIKit iOS 27 scene lifecycle adoption.

This scanner does not edit the project.
It intentionally reports evidence and warnings for manual review.
"""

from __future__ import annotations

import argparse
import json
import plistlib
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

SKIP_DIRS = {
    ".git", ".build", "build", "DerivedData", "Pods", "Carthage",
    "node_modules", "vendor", "Vendor", ".swiftpm",
}

@dataclass
class Finding:
    severity: str
    code: str
    message: str
    evidence: str = ""

def walk_files(root: Path, suffixes: tuple[str, ...]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix in suffixes:
            yield p

def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def extract_balanced_body(text: str, start_index: int) -> str:
    brace = text.find("{", start_index)
    if brace == -1:
        return ""
    depth = 0
    for i in range(brace, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1:i]
    return text[brace + 1:]

def function_body_containing(text: str, needle: str) -> str:
    idx = text.find(needle)
    if idx == -1:
        return ""
    func_idx = text.rfind("func ", 0, idx)
    return extract_balanced_body(text, func_idx if func_idx != -1 else idx)

def helper_functions(text: str):
    # Good enough for private/local audit helpers.
    result = {}
    for m in re.finditer(r"\bfunc\s+([A-Za-z_]\w*)\s*\(", text):
        name = m.group(1)
        result.setdefault(name, []).append(extract_balanced_body(text, m.start()))
    return result

def parse_plists(root: Path):
    parsed = []
    for path in walk_files(root, (".plist",)):
        try:
            with path.open("rb") as f:
                data = plistlib.load(f)
            if isinstance(data, dict):
                parsed.append((path, data))
        except Exception:
            pass
    return parsed

def plist_scene_configs(data: dict):
    manifest = data.get("UIApplicationSceneManifest")
    if not isinstance(manifest, dict):
        return None, None
    configs = manifest.get("UISceneConfigurations")
    return manifest, configs if isinstance(configs, dict) else None

def has_static_window_config(plists):
    configs_found = []
    for path, data in plists:
        manifest, configs = plist_scene_configs(data)
        if manifest is None:
            continue
        role_configs = []
        if configs:
            value = configs.get("UIWindowSceneSessionRoleApplication")
            if isinstance(value, list):
                role_configs = [x for x in value if isinstance(x, dict)]
        configs_found.append((path, manifest, role_configs))
    return configs_found

def find_storyboard(root: Path, name: str):
    wanted = name + ".storyboard"
    for p in walk_files(root, (".storyboard",)):
        if p.name == wanted:
            return p
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Path to the iOS project/repository")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.project).expanduser().resolve()
    if not root.exists():
        print(f"Project path does not exist: {root}", file=sys.stderr)
        return 2

    findings: list[Finding] = []

    swift_files = list(walk_files(root, (".swift",)))
    swift_texts = [(p, read_text(p)) for p in swift_files]
    all_swift = "\n".join(t for _, t in swift_texts)

    appdelegate_files = [(p, t) for p, t in swift_texts if "UIApplicationDelegate" in t]
    scenedelegate_files = [(p, t) for p, t in swift_texts if "UIWindowSceneDelegate" in t or "UISceneDelegate" in t]

    swiftui_main = bool(re.search(r"@main[\s\S]{0,300}\bstruct\s+\w+\s*:\s*App\b", all_swift))
    uikit_main = any("@main" in t and "UIApplicationDelegate" in t for _, t in appdelegate_files)

    if swiftui_main and not uikit_main:
        verdict = "PASS"
        findings.append(Finding(
            "info", "SWIFTUI_APP_LIFECYCLE",
            "Pure SwiftUI App lifecycle detected; UIKit SceneDelegate migration is not directly applicable."
        ))
        return emit(verdict, findings, root, args.json)

    plists = parse_plists(root)
    static_configs = has_static_window_config(plists)

    static_valid = False
    static_delegate_names = []
    storyboard_names = []

    if static_configs:
        for path, manifest, role_configs in static_configs:
            if role_configs:
                static_valid = True
                for cfg in role_configs:
                    delegate = cfg.get("UISceneDelegateClassName")
                    storyboard = cfg.get("UISceneStoryboardFile")
                    if isinstance(delegate, str):
                        static_delegate_names.append(delegate)
                    if isinstance(storyboard, str):
                        storyboard_names.append(storyboard)
                findings.append(Finding(
                    "info", "STATIC_SCENE_CONFIGURATION",
                    "Static UIWindow scene configuration found.",
                    str(path)
                ))
            else:
                findings.append(Finding(
                    "high", "EMPTY_SCENE_CONFIGURATION",
                    "UIApplicationSceneManifest exists but has no Window Application scene configuration.",
                    str(path)
                ))

    appdelegate_text = "\n".join(t for _, t in appdelegate_files)
    dynamic_config = "configurationForConnecting" in appdelegate_text and "UISceneConfiguration" in appdelegate_text

    if not static_valid and not dynamic_config:
        findings.append(Finding(
            "critical", "NO_USABLE_SCENE_CONFIGURATION",
            "UIKit app has no usable static UIScene configuration and no detected dynamic configurationForConnecting implementation. This is an iOS 27 launch-compliance risk."
        ))

    if static_valid and not dynamic_config:
        findings.append(Finding(
            "info", "STATIC_CONFIG_IS_SUFFICIENT",
            "No configurationForConnecting implementation detected, but a static Info.plist scene configuration exists. This is valid when dynamic scene selection is not needed."
        ))

    if dynamic_config:
        findings.append(Finding(
            "info", "DYNAMIC_SCENE_CONFIGURATION",
            "application(_:configurationForConnecting:options:) detected."
        ))

    if not scenedelegate_files:
        if static_valid or dynamic_config:
            findings.append(Finding(
                "critical", "SCENE_DELEGATE_MISSING",
                "Scene lifecycle configuration exists, but no Swift type conforming to UISceneDelegate/UIWindowSceneDelegate was detected."
            ))
    else:
        for p, t in scenedelegate_files:
            if "UIWindowSceneDelegate" in t:
                findings.append(Finding(
                    "info", "WINDOW_SCENE_DELEGATE_FOUND",
                    "UIWindowSceneDelegate implementation detected.",
                    str(p)
                ))
            if re.search(r"\bvar\s+window\s*:\s*UIWindow\?", t):
                findings.append(Finding(
                    "info", "SCENE_WINDOW_PROPERTY",
                    "Scene delegate contains a UIWindow property.",
                    str(p)
                ))

    # Window ownership mode
    storyboard_mode = bool(storyboard_names)
    manual_window_creation = any("UIWindow(windowScene:" in t.replace(" ", "") or "UIWindow(windowScene:" in t for _, t in scenedelegate_files)
    # More reliable whitespace-tolerant expression:
    manual_window_creation = manual_window_creation or any(re.search(r"UIWindow\s*\(\s*windowScene\s*:", t) for _, t in scenedelegate_files)

    if storyboard_mode:
        for name in sorted(set(storyboard_names)):
            sb = find_storyboard(root, name)
            if sb is None:
                findings.append(Finding(
                    "high", "SCENE_STORYBOARD_NOT_FOUND",
                    f"Scene configuration references storyboard '{name}', but {name}.storyboard was not found."
                ))
            else:
                sb_text = read_text(sb)
                if "initialViewController=" not in sb_text:
                    findings.append(Finding(
                        "high", "NO_INITIAL_VIEW_CONTROLLER",
                        f"{name}.storyboard is used as the scene storyboard but no initialViewController marker was detected.",
                        str(sb)
                    ))
                else:
                    findings.append(Finding(
                        "info", "STORYBOARD_WINDOW_MODE",
                        f"Storyboard-driven scene detected: {name}.storyboard.",
                        str(sb)
                    ))
        if manual_window_creation:
            findings.append(Finding(
                "medium", "MIXED_WINDOW_OWNERSHIP",
                "UISceneStoryboardFile is configured and SceneDelegate also appears to create UIWindow(windowScene:). Review for duplicate/unnecessary window ownership before changing anything."
            ))
    else:
        if static_valid or dynamic_config:
            if not manual_window_creation:
                findings.append(Finding(
                    "high", "PROGRAMMATIC_WINDOW_NOT_DETECTED",
                    "No UISceneStoryboardFile is configured and no UIWindow(windowScene:) creation was detected in SceneDelegate. Verify how the root window is created."
                ))
            else:
                findings.append(Finding(
                    "info", "PROGRAMMATIC_WINDOW_MODE",
                    "Programmatic UIWindow(windowScene:) creation detected."
                ))

    # Legacy AppDelegate lifecycle callbacks
    legacy_map = {
        "applicationDidBecomeActive": "sceneDidBecomeActive",
        "applicationWillResignActive": "sceneWillResignActive",
        "applicationDidEnterBackground": "sceneDidEnterBackground",
        "applicationWillEnterForeground": "sceneWillEnterForeground",
    }
    for p, t in appdelegate_files:
        for old, new in legacy_map.items():
            if old in t:
                body = function_body_containing(t, old)
                if body.strip():
                    findings.append(Finding(
                        "high", "LEGACY_UI_LIFECYCLE_CALLBACK",
                        f"{old} contains behavior in AppDelegate. With scene lifecycle, review and migrate scene-specific behavior to {new}.",
                        str(p)
                    ))

    # AppDelegate window usage
    for p, t in appdelegate_files:
        if re.search(r"\bvar\s+window\s*:\s*UIWindow\?", t):
            findings.append(Finding(
                "low", "APPDELEGATE_WINDOW_PRESENT",
                "AppDelegate has a legacy UIWindow property. This is not automatically wrong, but scene-based apps should not assume it is the active UI window.",
                str(p)
            ))
        if re.search(r"\bself\.window\b|\bwindow\?\.rootViewController\b|\bgetMainWindow\s*\(", t):
            findings.append(Finding(
                "medium", "APPDELEGATE_WINDOW_USED_FOR_UI",
                "AppDelegate window is used or exposed for UI access. Verify consumers use the active SceneDelegate window after scene adoption.",
                str(p)
            ))

    # Unsafe scene lookup
    for p, t in swift_texts:
        if re.search(r"connectedScenes\s*\.first\b", t):
            findings.append(Finding(
                "medium", "FIRST_CONNECTED_SCENE",
                "connectedScenes.first detected. It may select a non-active scene; review UI/navigation paths and prefer the foreground-active UIWindowScene.",
                str(p)
            ))

    # didFinish launch-time UI access, including one-level helper calls
    ui_tokens = (
        "connectedScenes", "rootViewController", "overrideUserInterfaceStyle",
        "makeKeyAndVisible", "SceneDelegate", "self.window", "window?."
    )
    for p, t in appdelegate_files:
        did_body = function_body_containing(t, "didFinishLaunchingWithOptions")
        if not did_body:
            continue
        direct = [token for token in ui_tokens if token in did_body]
        if direct:
            findings.append(Finding(
                "high", "UI_ACCESS_DURING_DID_FINISH",
                "didFinishLaunchingWithOptions directly accesses scene/window UI. The scene may not be connected yet.",
                f"{p}: {', '.join(direct)}"
            ))

        funcs = helper_functions(t)
        called_names = set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", did_body))
        for name in sorted(called_names):
            for body in funcs.get(name, []):
                touched = [token for token in ui_tokens if token in body]
                if touched:
                    findings.append(Finding(
                        "high", "UI_HELPER_CALLED_DURING_DID_FINISH",
                        f"didFinishLaunchingWithOptions calls '{name}()', which accesses scene/window UI. Move only the window-dependent behavior to SceneDelegate.",
                        f"{p}: {', '.join(touched)}"
                    ))

    # URL/deep link review
    url_schemes = []
    for path, data in plists:
        for item in data.get("CFBundleURLTypes", []) if isinstance(data.get("CFBundleURLTypes"), list) else []:
            if isinstance(item, dict):
                schemes = item.get("CFBundleURLSchemes")
                if isinstance(schemes, list):
                    url_schemes.extend(str(s) for s in schemes)

    if url_schemes:
        has_app_open = "open url:" in appdelegate_text or "openURL" in appdelegate_text or "UIApplication.OpenURLOptionsKey" in appdelegate_text
        scene_text = "\n".join(t for _, t in scenedelegate_files)
        has_scene_open = "openURLContexts" in scene_text
        if has_app_open and not has_scene_open and (static_valid or dynamic_config):
            findings.append(Finding(
                "high", "URL_CALLBACK_SCENE_REVIEW",
                "Custom URL schemes exist and AppDelegate URL handling was detected, but SceneDelegate openURLContexts was not detected. Review deep-link/SDK callback routing after scene adoption.",
                ", ".join(sorted(set(url_schemes)))
            ))
        elif has_scene_open:
            findings.append(Finding(
                "info", "SCENE_URL_HANDLER_FOUND",
                "SceneDelegate openURLContexts handler detected.",
                ", ".join(sorted(set(url_schemes)))
            ))
        else:
            findings.append(Finding(
                "medium", "URL_SCHEMES_REQUIRE_MANUAL_REVIEW",
                "Custom URL schemes exist. Verify their callback owner and cold/warm launch behavior.",
                ", ".join(sorted(set(url_schemes)))
            ))

    # Push navigation + connected scene warning is covered above; note push registration.
    if "UNUserNotificationCenterDelegate" in all_swift or "MessagingDelegate" in all_swift:
        findings.append(Finding(
            "info", "PUSH_INTEGRATION_DETECTED",
            "Push notification integration detected. Preserve registration/token code; separately validate any notification-driven UI navigation against the active scene."
        ))

    # Determine verdict
    severities = {f.severity for f in findings}
    if "critical" in severities:
        verdict = "NEEDS MIGRATION"
    elif "high" in severities:
        verdict = "REVIEW REQUIRED"
    elif "medium" in severities or "low" in severities:
        verdict = "PASS WITH WARNINGS"
    else:
        verdict = "PASS"

    return emit(verdict, findings, root, args.json)

def emit(verdict: str, findings: list[Finding], root: Path, as_json: bool):
    payload = {
        "project": str(root),
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"iOS 27 Scene Lifecycle Audit")
        print(f"Project: {root}")
        print(f"Verdict: {verdict}")
        print()
        order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        for f in sorted(findings, key=lambda x: order.get(x.severity, 9)):
            print(f"[{f.severity.upper()}] {f.code}")
            print(f"  {f.message}")
            if f.evidence:
                print(f"  Evidence: {f.evidence}")
            print()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

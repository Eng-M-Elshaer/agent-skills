---
name: ios-27-scene-lifecycle-audit
description: Audit an existing UIKit iOS project for the iOS 27 scene-based lifecycle requirement. Use when checking AppDelegate, SceneDelegate, Info.plist, storyboard/programmatic window setup, lifecycle callbacks, deep links, push-navigation, or launch-crash risk before building with the iOS 27 SDK. Produces a read-only verdict and a minimal, regression-safe remediation plan before any code changes.
---

# iOS 27 Scene Lifecycle Audit

Audit an existing iOS project for correct UIKit scene lifecycle adoption and produce the smallest safe migration plan.

## Core principle

**Audit first. Do not edit by default.**

The goal is not to modernize the project broadly. The goal is to make the app compliant with the iOS 27 scene lifecycle requirement while preserving its current behavior.

Never change navigation architecture, initial screens, authentication flow, notification routing, payment callbacks, SDK initialization order, app appearance, background behavior, or URL handling unless the audit proves a scene-lifecycle change is required.

If the project is already compliant, say so and recommend no required code changes.

## When to use

Use this skill when the user asks to:

- check whether an existing UIKit app has the iOS 27 `UIScene` / `SceneDelegate` problem;
- investigate a launch crash or launch assertion related to `UIScene`;
- migrate an older UIKit app to scene-based lifecycle;
- review `AppDelegate.swift`, `SceneDelegate.swift`, `Info.plist`, or storyboard scene configuration;
- prepare a safe upgrade to the latest iOS SDK without breaking existing behavior;
- check whether lifecycle callbacks, deep links, push notifications, payment redirects, or UI setup are in the correct delegate.

Do not use this skill for a pure SwiftUI app whose entry point is an `@main` type conforming to `SwiftUI.App`, unless the app also embeds a UIKit app delegate and the request specifically concerns it.

## Authoritative rule

For UIKit apps built with the iOS 27 SDK, scene-based lifecycle adoption is required.

A valid project must provide scene configuration in one of these ways:

1. **Static configuration** in `Info.plist` using `UIApplicationSceneManifest` → `UISceneConfigurations`; or
2. **Dynamic configuration** from `UIApplicationDelegate.application(_:configurationForConnecting:options:)`.

Static `Info.plist` configuration is sufficient by itself when it contains the required scene configuration. Do not require `configurationForConnecting` merely for style if a valid static configuration already exists.

## Operating modes

### Default: Audit mode

Read project files and produce findings only. Make no edits.

### Plan mode

After the audit, produce exact file-by-file changes, preserving current behavior.

### Apply mode

Only enter Apply mode if the user explicitly asks to modify the project. Before editing:

1. show the audit verdict;
2. show the minimal change set;
3. identify behavior that must remain unchanged;
4. define regression tests;
5. then edit only the required lines.

## Step 1 — Identify the app lifecycle

Inspect:

- `AppDelegate.swift` / Objective-C equivalent;
- `SceneDelegate.swift` / Objective-C equivalent;
- all candidate `Info.plist` files;
- target build settings in `project.pbxproj` when the plist is generated;
- main storyboard(s);
- SwiftUI `@main` declarations.

Classify the app as one of:

- `SWIFTUI_APP_LIFECYCLE`
- `UIKIT_SCENE_STATIC`
- `UIKIT_SCENE_DYNAMIC`
- `UIKIT_SCENE_INCOMPLETE`
- `UIKIT_LEGACY_NO_SCENES`
- `UNKNOWN_REVIEW_REQUIRED`

If the project contains multiple application targets, audit each target independently. Never assume one plist applies to every target.

## Step 2 — Run the static scanner

From the skill directory:

```bash
python3 scripts/audit_scene_lifecycle.py /path/to/project
```

For machine-readable output:

```bash
python3 scripts/audit_scene_lifecycle.py /path/to/project --json
```

Treat scanner output as evidence, not as the final conclusion. Review relevant source manually before deciding.

## Step 3 — Check `Info.plist` scene configuration

For a UIKit app, inspect `UIApplicationSceneManifest`.

A typical single-scene static configuration is:

```xml
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <false/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>UIWindowSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneConfigurationName</key>
                <string>Default Configuration</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>
```

A storyboard-driven app may additionally contain:

```xml
<key>UISceneStoryboardFile</key>
<string>Main</string>
```

### Hard failure conditions

Mark `NEEDS MIGRATION` when a UIKit app has neither:

- a usable static scene configuration in the target's effective Info.plist; nor
- a usable dynamic `configurationForConnecting` implementation.

Also mark `NEEDS MIGRATION` when the configuration references a scene delegate that doesn't exist or doesn't conform to `UIWindowSceneDelegate`.

## Step 4 — Determine window ownership

This is critical. Do not mix window strategies accidentally.

### A. Storyboard-driven scene

If `UISceneStoryboardFile` is configured:

- UIKit creates the scene window and installs the storyboard's initial view controller.
- `SceneDelegate.window` should receive that window.
- `scene(_:willConnectTo:options:)` may adjust or replace the root, but should not create a second `UIWindow` without a specific reason.
- verify the storyboard has an initial view controller.

If the project both declares `UISceneStoryboardFile` and creates `UIWindow(windowScene:)`, report:

`WARNING — mixed window ownership`

Do not automatically remove either one. First determine which behavior is currently intended.

### B. Programmatic scene

If there is no `UISceneStoryboardFile`:

`SceneDelegate` should normally create the window in:

```swift
func scene(
    _ scene: UIScene,
    willConnectTo session: UISceneSession,
    options connectionOptions: UIScene.ConnectionOptions
) {
    guard let windowScene = scene as? UIWindowScene else { return }

    let window = UIWindow(windowScene: windowScene)
    window.rootViewController = ExistingRootViewController()
    window.makeKeyAndVisible()
    self.window = window
}
```

Preserve the exact existing root decision logic. Do not replace login/onboarding/tab-bar logic with a new architecture.

## Step 5 — Check lifecycle callback placement

Once the app adopts scene lifecycle, UI lifecycle events belong in `UISceneDelegate`.

Look for these old `UIApplicationDelegate` callbacks:

- `applicationDidBecomeActive`
- `applicationWillResignActive`
- `applicationDidEnterBackground`
- `applicationWillEnterForeground`

If they contain real behavior, map them carefully to:

- `sceneDidBecomeActive`
- `sceneWillResignActive`
- `sceneDidEnterBackground`
- `sceneWillEnterForeground`

Do not blindly move process-global work. Distinguish:

### Keep in `AppDelegate`

Examples:

- Firebase initialization;
- SDK initialization that is process-wide;
- push registration;
- dependency/container bootstrap;
- global logging/analytics bootstrap;
- background task registration when it is app-level;
- application termination handling where still appropriate.

### Move or route through `SceneDelegate`

Examples:

- changing the active window/root controller;
- UI appearance that requires a scene/window;
- presenting alerts on the current UI;
- starting/stopping scene-specific UI work;
- per-scene foreground/background UI behavior.

If aggregate app state is required rather than per-scene state, consider `UIApplication` lifecycle notifications instead of assuming one scene represents the entire process.

## Step 6 — Check launch-time UI access

Inspect `application(_:didFinishLaunchingWithOptions:)` and every helper it calls.

Flag UI operations that require a connected scene, including:

- `UIApplication.shared.connectedScenes`;
- `SceneDelegate.window`;
- `window.rootViewController`;
- `overrideUserInterfaceStyle` on a scene window;
- presenting view controllers or alerts;
- changing the root controller.

A helper called from `didFinishLaunching` is still launch-time UI access even if the UI code is hidden in a private method.

Recommended fix:

- keep process initialization in `didFinishLaunching`;
- move window-dependent behavior to `scene(_:willConnectTo:options:)`, `sceneWillEnterForeground`, or `sceneDidBecomeActive`, depending on semantics.

Preserve execution order for unrelated SDK initialization.

## Step 7 — Check unsafe window lookup

Flag:

```swift
UIApplication.shared.connectedScenes.first
```

and similar "first window" patterns.

They are not automatically fatal for a single-scene app, but they are brittle. Prefer resolving the active foreground `UIWindowScene` or, even better, passing the relevant scene/window from the current context.

Safe fallback pattern for an existing single-scene architecture:

```swift
let activeWindowScene = UIApplication.shared.connectedScenes
    .compactMap { $0 as? UIWindowScene }
    .first { $0.activationState == .foregroundActive }

let sceneDelegate = activeWindowScene?.delegate as? SceneDelegate
let window = sceneDelegate?.window
```

Do not replace every lookup automatically. Change only code paths that need safe active-window resolution.

## Step 8 — Check `AppDelegate.window`

If the app uses scenes, inspect any `AppDelegate.window` property.

It may be legacy and may remain `nil` or no longer represent the active UI.

Flag as higher risk when code:

- returns `AppDelegate.window` from a protocol/service;
- presents UI from `AppDelegate.window`;
- uses it to determine the current root controller;
- changes appearance through it.

Before replacing it, identify all consumers and preserve their behavior by routing them to the correct scene window.

## Step 9 — Check deep links and SDK callbacks

If the app has URL schemes, payment redirects, authentication callbacks, Facebook/Google/TikTok/Stripe integrations, or other URL handling, verify that scene adoption did not strand the callback in an app-delegate-only path.

Inspect for:

- `application(_:open:options:)`;
- `scene(_:openURLContexts:)`;
- `scene(_:continue:)`;
- `application(_:continue:restorationHandler:)`.

Do not move callbacks mechanically. Preserve each SDK's documented integration point and current routing behavior.

Create a callback inventory:

| Callback | Current owner | Trigger | Destination/side effect | Must preserve |
|---|---|---|---|---|

## Step 10 — Check push-notification navigation

Push registration and token handling can remain app-level.

UI navigation caused by a notification must resolve the correct scene/window.

Inspect:

- foreground notification presentation;
- notification tap;
- remote notification data handling;
- cold launch from notification;
- notification handling while another scene is active.

Do not rewrite notification payload parsing while migrating the lifecycle.

## Step 11 — Build the verdict

Use exactly one primary verdict:

### `PASS`

The app has valid scene adoption and no required iOS 27 migration is found.

Optional hardening can be listed separately, but do not call it required.

### `PASS WITH WARNINGS`

The app satisfies the scene requirement but contains brittle or duplicated patterns such as:

- `connectedScenes.first`;
- both storyboard-created and manually-created windows;
- legacy `AppDelegate.window`;
- launch-time helper that may access UI before scene connection.

### `REVIEW REQUIRED`

Static analysis can't establish the target's effective scene configuration or behavior safely.

### `NEEDS MIGRATION`

The UIKit app lacks a valid scene lifecycle path or has a configuration defect likely to prevent correct launch with the iOS 27 SDK.

## Step 12 — Produce the report

Always return these sections:

### 1. Verdict

One line with the primary verdict and a short reason.

### 2. Evidence

Show exact files and code/configuration that led to the result.

### 3. Required changes

Only changes needed for iOS 27 compliance.

If none:

`No required scene-lifecycle code changes found.`

### 4. Recommended hardening

Optional changes that reduce risk but are not required for launch compliance.

Clearly separate them from required changes.

### 5. Behavior preservation list

List project behaviors that must remain identical after any migration, based on what the project actually contains.

Examples:

- logged-in vs logged-out root;
- splash/onboarding;
- theme selection;
- push routing;
- payment callback;
- universal/custom links;
- Facebook/Google/TikTok/Stripe callbacks;
- VoIP/CallKit;
- background tasks;
- forced-update alert.

Do not invent features not found in the project.

### 6. Minimal safe implementation plan

Use the phased plan in `references/remediation-playbook.md`.

Every step must say:

- file;
- exact change;
- why;
- risk;
- validation after the step.

### 7. Regression test matrix

Use `references/test-matrix.md` and include only applicable tests.

### 8. Rollback plan

Define how to revert the migration safely.

## Migration safety rules

1. **Do not refactor unrelated code.**
2. **Do not change the root navigation flow unless required.**
3. **Do not rename notification keys, URL schemes, storyboard IDs, or SDK callbacks.**
4. **Do not change `UIApplicationSupportsMultipleScenes` from `false` to `true` unless the product explicitly wants multi-window support.**
5. **Do not remove `UISceneStoryboardFile` merely because programmatic root replacement exists; first determine the intended window ownership.**
6. **Do not add `configurationForConnecting` when static plist configuration is already valid unless dynamic scene selection is needed.**
7. **Do not move process-wide SDK initialization into `SceneDelegate`.**
8. **Do not leave UI lifecycle logic in deprecated app delegate callbacks after scene adoption if the app relies on that logic.**
9. **Do not assume `connectedScenes.first` is the foreground scene.**
10. **Do not claim a crash is fixed until launch and lifecycle regression tests pass.**

## Safe change order

When migration is required, prefer this order:

1. capture baseline behavior;
2. make/confirm scene configuration;
3. make/confirm `SceneDelegate`;
4. establish exactly one window-ownership strategy;
5. preserve the current root controller logic;
6. migrate only scene-specific lifecycle behavior;
7. migrate/reroute UI callbacks that need the scene window;
8. harden active-window lookup where necessary;
9. build and run;
10. execute regression tests;
11. only then remove dead legacy code.

Never start by deleting old code.

## Reference files

- `references/remediation-playbook.md` — phased migration and rollback plan.
- `references/test-matrix.md` — regression test checklist.
- `scripts/audit_scene_lifecycle.py` — read-only static scanner.

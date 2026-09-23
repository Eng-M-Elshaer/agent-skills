# iOS 27 Scene Lifecycle — Minimal Safe Remediation Playbook

Use this playbook only after the audit identifies a required change or a clearly justified warning.

## Phase 0 — Freeze the baseline

Before changing code:

1. Confirm the working tree is clean or create a dedicated migration branch.
2. Record the current build configuration, deployment target, Xcode version, and SDK.
3. Build the current app before changing anything.
4. Capture current startup behavior:
   - fresh install;
   - logged out;
   - logged in;
   - app reopened from background.
5. Capture every external entry path found in the project:
   - notification tap;
   - custom URL scheme;
   - universal link;
   - payment callback;
   - social-login callback;
   - VoIP/call flow;
   - background task.
6. Record current initial/root view controller behavior.

Do not continue if the existing baseline is already broken without documenting it.

## Phase 1 — Decide scene configuration strategy

Choose exactly one primary strategy.

### Strategy A — Static Info.plist configuration

Use when the app has a normal fixed scene configuration.

Required elements:

- `UIApplicationSceneManifest`;
- `UISceneConfigurations`;
- `UIWindowSceneSessionRoleApplication`;
- scene configuration name;
- scene delegate class;
- storyboard name when storyboard-driven.

`configurationForConnecting` is optional when static configuration is complete.

### Strategy B — Dynamic AppDelegate configuration

Use when the app intentionally chooses different scene configuration at runtime.

Implement `application(_:configurationForConnecting:options:)` and return a complete `UISceneConfiguration`.

Avoid creating a dynamic configuration just to duplicate a correct static plist.

## Phase 2 — Decide window ownership

### Storyboard-owned window

Keep `UISceneStoryboardFile`.

Expected behavior:

- UIKit creates the window;
- UIKit attaches the storyboard initial view controller;
- `SceneDelegate.window` is available;
- `willConnectTo` may customize the existing window.

Do not create a second window unless intentionally replacing window ownership.

### Programmatic window

Do not rely on `UISceneStoryboardFile` for the scene's initial window.

In `scene(_:willConnectTo:options:)`:

1. cast `UIScene` to `UIWindowScene`;
2. create `UIWindow(windowScene:)`;
3. run the existing root decision;
4. call `makeKeyAndVisible`;
5. retain the window in `SceneDelegate.window`.

Preserve the same splash/login/onboarding/tab-bar selection logic.

## Phase 3 — Move only UI lifecycle responsibilities

Create an inventory before moving anything.

| Existing callback/code | Process-global? | Scene/UI-specific? | Destination |
|---|---:|---:|---|
| Firebase configure | Yes | No | AppDelegate |
| Push registration | Yes | No | AppDelegate |
| UI theme on window | No | Yes | SceneDelegate |
| Root controller change | No | Yes | SceneDelegate |
| Foreground UI refresh | Usually no | Yes | sceneWillEnterForeground / sceneDidBecomeActive |
| Background UI cleanup | Usually no | Yes | sceneDidEnterBackground |

Preserve behavior, not just method names.

## Phase 4 — Fix window access safely

Search for:

- `AppDelegate.window`;
- `connectedScenes.first`;
- `UIApplication.shared.windows`;
- root/presentation logic detached from a scene.

For each occurrence:

1. identify which user flow calls it;
2. identify which scene should own the UI;
3. pass the scene/window directly where practical;
4. otherwise resolve the active foreground `UIWindowScene`;
5. validate the exact flow immediately.

Do not perform a project-wide replacement without per-call review.

## Phase 5 — Preserve external entry points

For every URL scheme, push type, payment callback, or authentication callback:

1. note current handler;
2. note payload/URL shape;
3. note destination screen or side effect;
4. migrate only the lifecycle routing needed;
5. keep payload parsing unchanged;
6. test cold, warm, and foreground cases where applicable.

## Phase 6 — Build validation

Validate with the iOS 27 SDK:

1. clean build;
2. launch simulator/device;
3. confirm no UIScene lifecycle assertion;
4. confirm root controller;
5. background/foreground three times;
6. terminate and relaunch;
7. rotate / resize where supported;
8. verify no duplicate windows or duplicate initial-screen flashes.

Also test at least one supported older OS version if the app still supports it.

## Phase 7 — Feature regression

Run only applicable rows from `test-matrix.md`.

A migration is incomplete if launch works but any pre-existing entry flow breaks.

## Phase 8 — Cleanup last

Only after tests pass:

- remove dead app-delegate lifecycle methods;
- remove genuinely unused legacy window code;
- remove duplicated scene configuration;
- reduce optional warnings.

Do not combine cleanup with the initial compliance patch when a smaller patch is possible.

## Rollback plan

Before edits:

- create a branch or commit checkpoint.

If any regression appears:

1. revert only the latest migration phase;
2. confirm the baseline behavior returns;
3. isolate the failing entry path;
4. revise the plan;
5. reapply the smallest change.

Never "fix forward" by rewriting navigation architecture during this migration.

<skill>
<name>rules-enforcer</name>
<path>/Users/restart/.codex/skills/rules-enforcer/SKILL.md</path>
---
name: rules-enforcer
description: Enforce architecture/style rules when coding
metadata:
  short-description: Enforce architecture/style rules when coding
---

# Rules Enforcer Skill

This skill contains explicit rules that Codex must follow when generating or modifying code for the project. These rules enforce the architecture and style principles identified by the other skills and add project‑specific constraints.

## Core Principles

1. **Separation of concerns**: Keep the UI, state management, data access, and business logic separate. Widgets should only handle layout and user interaction; they must not contain business logic or direct calls to APIs. All business logic belongs in view models or cubits, and all data access must go through repositories【288429638864479†L775-L804】.
2. **Repository pattern**: Every data source must be represented by a repository class. Repositories abstract away services and provide domain models to view models【288429638864479†L789-L804】. Repositories should be abstract and allow multiple implementations (e.g., development vs staging)【755528024047531†L762-L769】. Services wrap API endpoints and expose asynchronous responses without holding state【288429638864479†L845-L857】. Repositories must not know about each other【288429638864479†L818-L820】.
3. **State management**: Use a single state management approach consistently across the project (e.g., `Cubit` with `Bloc` or `Riverpod`). View models/cubits are responsible for retrieving data from repositories, transforming it, maintaining UI state, and exposing commands【288429638864479†L742-L758】. Do not mix different state management libraries arbitrarily.
4. **Dependency injection**: Do not instantiate dependencies directly inside widgets or view models. Use a DI container (`provider` or `get_it`) to manage all dependencies【755528024047531†L730-L735】. Register repositories, services, and view models in one central file and use the DI system to resolve them.
5. **Navigation**: Use `go_router` for navigation (recommended for most apps)【755528024047531†L736-L744】. Define routes in a single file or set of files; avoid scattered `Navigator.push` calls. When necessary to use the `Navigator` API directly, wrap it in a navigation service.
6. **Naming and organization**: Follow the naming conventions detected by the style skill. Classes should have suffixes that describe their role (e.g., `HomeScreen`, `HomeViewModel`, `HomeRepository`, `HomeService`). File names and directories must use `lowercase_with_underscores`【964970052002181†L393-L405】. Place shared UI widgets in `ui/core/` rather than a generic `widgets` folder【755528024047531†L746-L760】. Each feature should live in its own folder with subfolders for `ui`, `state`, `data`, and `domain`.
7. **Networking and API calls**: Use `Dio` together with a code‑generation library like `Retrofit` for REST APIs. Service classes should wrap API endpoints and return `Future` or `Stream` objects. Do not call network APIs directly in view models or widgets.
8. **Models and immutability**: Define model classes using `freezed` and annotate them with `json_serializable` for JSON conversion. Do not edit generated files by hand. Always run `build_runner` to regenerate code after updating model classes.
9. **Localization and internationalization**: All user‑visible strings must come from the localization system. Support right‑to‑left (RTL) layouts; ensure your app’s root widget sets `locale` and `supportedLocales` appropriately and wrap top-level widgets in a `Directionality` widget when necessary.
10. **Asynchronous work**: Heavy asynchronous tasks (e.g., file I/O, complex computations) must run in `compute()` or an isolate. Do not perform blocking operations in the UI thread.
11. **Testing**: Write unit tests for every service, repository, and view model and widget tests for views【755528024047531†L771-L786】. Use fakes or mocks for testing dependencies to encourage modular, testable code【755528024047531†L789-L795】. Ensure that test files follow the same naming conventions as source files.
12. **Linting and formatting**: Use the `flutter_lints` package and configure `analysis_options.yaml` to enforce style rules【755528024047531†L815-L817】. Always run `dart format` on code before committing.

## Enforcement

Codex must apply these rules when reading, modifying, or generating code:

- **Before coding**: Read the architecture and style summaries. Confirm that any new class, file, or method respects the patterns and conventions defined there.
- **While coding**: Do not violate separation of concerns. When writing a widget, check if the logic belongs in a view model or repository. When writing a new repository, ensure it is abstract and uses a service for data access. Use DI to obtain dependencies.
- **After coding**: Review the changes against the rules. If any rule is violated, adjust the code or produce a recommendation for the user. For example, if a new screen includes API calls, extract them into a repository and service. If a file is named using the wrong case, rename it. If a localization string is hard‑coded, move it into the localization system.

This skill codifies the project’s constraints so that Codex always generates consistent and maintainable code.
</skill>

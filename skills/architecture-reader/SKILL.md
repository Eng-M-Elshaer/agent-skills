<skill>
<name>architecture-reader</name>
<path>/Users/restart/.codex/skills/architecture-reader/SKILL.md</path>
---
name: architecture-reader
description: Analyze Flutter/Dart project architecture
metadata:
  short-description: Analyze Flutter/Dart project architecture
---

# Architecture Reader Skill

This skill helps Codex understand the architecture of a Flutter/Dart project and produce a clear mental model before editing code. It analyzes the directory structure, layers, and relationships between components and produces a dependency graph and summary.

## Goals

1. **Identify architecture pattern**: Determine whether the project uses MVVM, Clean Architecture, or other patterns by looking for features such as `view_model`, `cubit`, `bloc`, `provider`, `repository`, `service`, `use_case`, or domain layers.
2. **Map the layers**: Recognize the UI layer (screens/views), state management layer (view models, cubits, blocs), data layer (repositories and services), and optional domain layer (use cases/interactors). A view model’s responsibilities include retrieving data from repositories, transforming it for presentation, maintaining UI state, and exposing commands that the view can call【288429638864479†L742-L758】. Repositories form the source of truth for model data; they poll data from services and handle caching, error handling, refresh logic, and other business logic【288429638864479†L775-L804】. Services wrap external data sources and expose asynchronous responses without holding state【288429638864479†L845-L857】. Repositories and services have many-to-many relationships, and repositories should not be aware of each other【288429638864479†L818-L820】.
3. **Build a dependency graph**: Create a diagram showing how screens depend on state objects (view models/blocs/cubits), which depend on repositories, which depend on services. Identify app‑wide session state managed by repositories【288429638864479†L827-L839】.
4. **Detect dependency injection and navigation**: Note how dependencies are provided (e.g. `provider`, `get_it`) and how navigation is implemented (e.g. `go_router`). The Flutter team strongly recommends dependency injection to avoid global objects and suggests using the provider package for DI【755528024047531†L730-L735】. They also recommend `go_router` for navigation【755528024047531†L736-L744】.
5. **Check naming conventions**: Verify that classes are named for the architectural component they represent (e.g. `HomeViewModel`, `HomeScreen`, `UserRepository`, `ClientApiService`) and that shared UI widgets live in `ui/core/` rather than a generic `widgets` folder【755528024047531†L746-L760】. Confirm that repository classes are abstract to allow multiple implementations【755528024047531†L762-L769】.
6. **Highlight testing responsibilities**: For each layer, suggest unit tests (services, repositories, view models) and widget tests for views【755528024047531†L771-L786】.

## Procedure

1. **Scan the project**: Examine the `lib/` directory, `pubspec.yaml`, and `analysis_options.yaml`. Identify modules (e.g., `features/`, `core/`, `shared/`), state management libraries (e.g., cubit, bloc, provider, riverpod), and third‑party packages (e.g., `dio`, `freezed`, `json_serializable`).
2. **Layer identification**:
   - **UI layer**: Files ending in `_screen.dart` or under `ui/` represent views. Document each screen and the state object it depends on.
   - **State layer**: Identify classes that extend `Cubit`, `Bloc`, `ChangeNotifier`, or `StateNotifier`. These are view models; list their responsibilities and the repositories they call.
   - **Data layer**: Find classes with `Repository` in their name. Note if they implement an abstract interface and which services they call. Record responsibilities like caching and error handling【288429638864479†L775-L804】.
   - **Service layer**: Find classes named `*Service` or in `service` folders. They wrap external APIs (REST, GraphQL, Firebase) and should not store state【288429638864479†L845-L857】.
   - **Domain layer (optional)**: Detect `use_case` or `interactor` classes that encapsulate complex business logic or combine multiple repositories.
3. **Dependency graph**: Create a hierarchical mapping: *View* → *ViewModel/Cubit/Bloc* → *Repository* → *Service*. Show many-to-many relationships where applicable【288429638864479†L818-L820】.
4. **Detect patterns**: Determine if the architecture follows MVVM (views + view models) or Clean Architecture (presentation, domain, data layers). Note any deviations (logic in widgets, direct calls to services).
5. **Provide recommendations**: If logic is found in widgets, suggest moving it to view models. If repositories are concrete classes, suggest introducing abstract interfaces【755528024047531†L762-L769】. Encourage using dependency injection and `go_router` where missing【755528024047531†L730-L744】. Recommend standardized naming conventions and directory structure【755528024047531†L746-L760】.
6. **Prepare summary**: Output a structured report with:
   - Architecture pattern identified.
   - Directory overview.
   - State management mechanism.
   - Dependency graph description.
   - Naming conventions used.
   - Recommendations for improvement.

Follow this procedure whenever Codex enters a new project so that it has a clear understanding of the project’s architecture before generating or modifying code.
</skill>

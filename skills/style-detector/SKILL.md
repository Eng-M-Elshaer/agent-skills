<skill>
<name>style-detector</name>
<path>/Users/restart/.codex/skills/style-detector/SKILL.md</path>
---
name: style-detector
description: Detect Flutter/Dart coding style and conventions
metadata:
  short-description: Detect Flutter/Dart coding style and conventions
---

# Style Detector Skill

This skill analyzes a Flutter/Dart project to learn its coding style and naming conventions. It extracts patterns from the existing code so that Codex can generate code that matches the project's style.

## Goals

1. **Identify naming conventions**: Determine how types, variables, constants, files, and directories are named. Dart’s official style guide defines three primary case styles—`UpperCamelCase` for types, `lowerCamelCase` for variables/functions, and `lowercase_with_underscores` for file and directory names【964970052002181†L306-L314】. Types (classes, enums, typedefs, and type parameters) should use `UpperCamelCase`【964970052002181†L315-L323】. Packages, directories, and source files should be named using `lowercase_with_underscores`【964970052002181†L393-L405】. Class members, variables, parameters, and named parameters should use `lowerCamelCase`【964970052002181†L448-L456】. Constants should also use `lowerCamelCase`【964970052002181†L470-L477】. Acronyms and abbreviations longer than two letters should be capitalized like words to avoid ambiguity【964970052002181†L520-L528】. Confirm that the project adheres to these conventions and record any deviations.
2. **Inspect folder structure and file organization**: Check whether the project is organized by feature (e.g., `features/home/ui/`, `features/home/state/`, `features/home/data/`) or by layer (e.g., `presentation/`, `data/`, `domain/`). Identify how shared components are stored (e.g., `ui/core/` instead of a generic `widgets` folder【755528024047531†L746-L760】).
3. **Identify state management style**: Determine whether the project uses `Cubit`, `Bloc`, `Provider`, `Riverpod`, or another pattern. Note how state classes are named and where they live (e.g., `home_cubit.dart` in `features/home/state/`).
4. **Determine dependency injection approach**: Note if the project uses `provider`, `get_it`, `injectable`, or other DI solutions. The Flutter documentation strongly recommends using dependency injection and suggests the provider package【755528024047531†L730-L735】.
5. **Identify navigation style**: Note if the project uses `go_router` (recommended【755528024047531†L736-L744】) or the traditional `Navigator` API. Record how routes are named and organized.
6. **Analyze code style details**:
   - **Widget composition**: Check if large widgets are split into smaller widgets or functions. Encourage small, reusable widgets.
   - **Use of `const`**: Determine if constant widgets are marked with `const` for performance.
   - **Error handling**: Identify patterns for error handling (e.g., `Either` types, exceptions, `Result` classes) and ensure new code matches.
   - **Null safety**: Confirm that the project uses Dart’s null safety features (`?`, `!` operators).
   - **Imports and prefixes**: Ensure import prefixes use `lowercase_with_underscores`【964970052002181†L393-L405】.
   - **Linting**: Check whether `analysis_options.yaml` includes `flutter_lints`【755528024047531†L815-L817】 and record any custom lint rules. The lint package encourages good coding practices across a team【755528024047531†L815-L817】.

## Procedure

1. **Scan naming patterns**: Parse a representative sample of classes, variables, files, and directories. Extract the case style used for each and compare with Dart’s recommendations【964970052002181†L306-L314】【964970052002181†L315-L323】. Record the detected pattern.
2. **Record folder organization**: Note the primary structure (feature‑based vs layer‑based) and how shared code and themes are stored. Record naming patterns for feature directories and ensure they follow `lowercase_with_underscores`【964970052002181†L393-L405】.
3. **Extract coding patterns**: Identify common patterns such as use of `freezed` for models, `json_serializable`, `build_runner`, `riverpod` vs `cubit`, `Dio` for networking, etc. Note how network calls are structured and where they live.
4. **Document style**: Summarize conventions for:
   - Type names, file names, and identifiers.
   - State class naming (e.g., `HomeCubit`, `HomeViewModel`).
   - DI registration (e.g., using `get_it` or `provider`).
   - Navigation pattern (e.g., `go_router` vs `Navigator`).
   - Testing conventions (naming of test files, use of `mockito` or `fake_async`).
5. **Provide recommendations**: If the project deviates from official Dart style conventions, suggest aligning with them for consistency. For instance, rename files to `lowercase_with_underscores`【964970052002181†L393-L405】 or rename constants to lowerCamelCase【964970052002181†L470-L477】. Encourage using abstract repository classes【755528024047531†L762-L769】, dependency injection【755528024047531†L730-L735】, and `go_router`【755528024047531†L736-L744】. Recommend adopting `flutter_lints` to enforce style rules【755528024047531†L815-L817】.
6. **Produce a style profile**: Output a report describing the project's naming conventions, folder structure, state management, DI, navigation, and other patterns. Codex should refer to this style profile when generating or modifying code to ensure consistency.

## Mixed Style Detection

Projects may contain a mix of coding styles due to different developers or evolving architecture. When detecting style, do **not** average conflicting patterns blindly. Instead:

- Identify the **dominant style** used across most of the codebase (e.g., feature‑first directories with Cubit and repository pattern).
- Detect **local feature styles**: each feature (e.g., `auth`, `profile`, `chat`) may have its own structure or state management library. When modifying existing code in a specific feature, follow that feature’s local style rather than the global average.
- Distinguish between **legacy style** and **current target style**. Legacy code may use old patterns (e.g., flat `screens/` and `services/` folders with `setState`), while newer code uses modern patterns (e.g., feature‑first, MVVM with Cubit). When creating new code, follow the current target style, not the legacy style.
- If a conflict exists (e.g., two styles in the same area), document the conflict and recommend which style to follow. Output a warning in the style profile so that developers can decide on a consistent direction.

By following this skill, Codex learns the project's unique style and adopts it in future code generation.
</skill>

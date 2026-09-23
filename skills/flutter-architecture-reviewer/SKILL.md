---
name: flutter-architecture-reviewer
description: Review a Flutter/Dart project for Clean Architecture compliance with a core/ + features/ structure. Use when you need an architecture audit report covering structure/layering, dependency rule violations (UI→Logic→Data only), naming conventions, file size hotspots, networking/routing/state-management smells, reusability/duplication hints, and a scored, actionable refactor plan in Markdown (exportable to PDF).
---

# Flutter Architecture Reviewer

استخدم السكيل ده علشان تعمل مراجعة معمارية (Architecture Audit) لمشروع Flutter بالكامل وتطلع تقرير Markdown عملي فيه سكور + مخالفات + خطة Refactor.

## Tech Stack Baseline (المفروض يكون موجود)

المراجعة بتفترض مشروع عامل Clean Architecture + Cubit + Freezed + Dio + Retrofit + GetIt + Localization + ScreenUtil… إلخ.

لو عايز الـ baseline الرسمي للـ dependencies (بالنسخ المحدثة اللي متفقين عليها)، بص على:

`/Users/restart/.codex/skills/flutter-architecture-reviewer/references/dependencies_baseline.md`

## تشغيل سريع

من جذر الريبو:

```bash
python3 /path/to/flutter-architecture-reviewer/scripts/analyze_flutter_arch.py --root . --out architecture_report.md
```

لو المشروع Flutter جوه فولدر تاني:

```bash
python3 /path/to/flutter-architecture-reviewer/scripts/analyze_flutter_arch.py --root path/to/app --out architecture_report.md
```

## القواعد اللي بنراجع عليها (Target Architecture)

### Core

```text
lib/
└── core/
    ├── di/
    ├── networking/
    ├── routing/
    ├── helpers/
    ├── theming/
    └── widgets/
```

### Feature

```text
lib/
└── features/
    └── feature_name/
        ├── data/
        │   ├── models/
        │   ├── repos/
        │   └── data_sources/
        ├── logic/
        │   ├── cubit/
        │   └── state/
        └── ui/
            ├── screens/
            └── widgets/
```

## Dependency Rules

المسموح:

```text
UI -> Logic -> Data
```

الممنوع:

```text
Data -> UI
Logic -> UI
Core -> Feature
Feature -> Another Feature (direct imports)
```

## مراجعات إضافية (مختصر)

- **Naming**: `snake_case` للملفات مع أنماط زي `login_cubit.dart`, `login_state.dart`, `login_repo.dart`.
- **File size warnings** (افتراضيًا):
  - Screen > 500 lines
  - Cubit > 300 lines
  - Widget > 250 lines
  - Repository > 400 lines
- **Networking**: رصد `Dio()`/Raw requests بره طبقة data أو بره `core/networking`.
- **Routing**: رصد `Navigator.push*` المتناثر وعدم وجود تنظيم في `core/routing`.
- **State management**: رصد `setState` داخل screens وكمان cubits الضخمة.
- **Reusability hints**: قيم ألوان/EdgeInsets متكررة تقترح نقلها لـ `core/theming` أو `core/helpers`.

## مخرجات التقرير

السكريبت بيطلع تقرير Markdown فيه:
- جدول درجات `/10` لكل محور + Overall score
- Summary سريع
- قائمة Violations مع `file paths`
- Recommendations + Refactor Plan (High/Medium/Low)

## تصدير PDF (اختياري)

لو عندك `pandoc`:

```bash
pandoc architecture_report.md -o architecture_report.pdf
```

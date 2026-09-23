#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


IMPORT_RE = re.compile(r"^\s*import\s+['\"]([^'\"]+)['\"]\s*;")
PART_RE = re.compile(r"^\s*part\s+['\"]([^'\"]+)['\"]\s*;")
PART_OF_RE = re.compile(r"^\s*part\s+of\s+['\"]?([^'\";]+)['\"]?\s*;")
HTTP_RE = re.compile(r"https?://[^\s'\"\\)]+")
COLOR_HEX_RE = re.compile(r"0xFF[0-9A-Fa-f]{6}")
EDGEINSETS_RE = re.compile(r"EdgeInsets\\.(all|only|symmetric)\\(([^\\)]*)\\)")

DEPENDENCIES_BASELINE: dict[str, str] = {
    "cupertino_icons": "^1.0.2",
    "build_runner": "^2.4.7",
    "flutter_bloc": "^8.1.3",
    "freezed": "^2.4.5",
    "freezed_annotation": "^2.4.1",
    "get_it": "^7.6.4",
    "json_serializable": "^6.7.1",
    "json_annotation": "^4.8.1",
    "dio": "^5.3.3",
    "retrofit": "^4.0.3",
    "retrofit_generator": "^8.0.4",
    "pretty_dio_logger": "^1.3.1",
    "intl": "^0.19.0",
    "easy_localization": "^3.0.3",
    "flutter_native_splash": "^2.3.5",
    "flutter_svg": "^2.0.9",
    "flutter_screenutil": "^5.9.0",
    "firebase_core": "^2.27.0",
    "cached_network_image": "^3.3.1",
    "shared_preferences": "^2.2.3",
    "flutter_secure_storage": "^9.2.2",
    "shimmer": "^3.0.0",
}


DEFAULT_THRESHOLDS = {
    "screen": 500,
    "cubit": 300,
    "widget": 250,
    "repo": 400,
}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _count_lines(text: str) -> int:
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


def _rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)


def _is_dart_file(p: Path) -> bool:
    return p.is_file() and p.suffix == ".dart"


def _dart_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.dart") if p.is_file()]


def _classify_layer(rel_path: str) -> str:
    norm = rel_path.replace("\\", "/")
    if "/lib/core/" in f"/{norm}":
        return "core"
    if "/lib/features/" in f"/{norm}":
        if "/ui/" in norm:
            return "ui"
        if "/logic/" in norm:
            return "logic"
        if "/data/" in norm:
            return "data"
        return "feature-unknown"
    if norm.startswith("lib/"):
        return "lib-root"
    return "other"


def _feature_name(rel_path: str) -> str | None:
    norm = rel_path.replace("\\", "/")
    m = re.search(r"^lib/features/([^/]+)/", norm)
    return m.group(1) if m else None


def _file_kind(rel_path: str) -> str | None:
    p = rel_path.replace("\\", "/").lower()
    base = os.path.basename(p)
    if "/ui/screens/" in p or base.endswith("_screen.dart") or base.endswith("_page.dart"):
        return "screen"
    if base.endswith("_cubit.dart") or "/logic/cubit/" in p:
        return "cubit"
    if base.endswith("_repo.dart") or base.endswith("_repository.dart") or "/data/repos/" in p:
        return "repo"
    if "/ui/widgets/" in p or base.endswith("_widget.dart") or base.endswith("_button.dart"):
        return "widget"
    return None


def _iter_imports(text: str) -> Iterable[str]:
    for line in text.splitlines():
        m = IMPORT_RE.match(line)
        if m:
            yield m.group(1)


def _resolve_import(root: Path, file_path: Path, imp: str) -> Path | None:
    # Only resolve repo-local imports. Skip dart:, package: (except same package via lib), etc.
    if imp.startswith("dart:") or imp.startswith("package:"):
        # Try to map package:<pkg>/<path> to <root>/<path> if it looks like a lib path.
        m = re.match(r"^package:[^/]+/(.+)$", imp)
        if not m:
            return None
        candidate = root / m.group(1)
        if candidate.exists():
            return candidate
        candidate2 = root / "lib" / m.group(1)
        if candidate2.exists():
            return candidate2
        return None

    if imp.startswith("/"):
        return None

    if imp.startswith("../") or imp.startswith("./"):
        candidate = (file_path.parent / imp).resolve()
        if candidate.exists():
            return candidate
        # If it's a folder import without .dart, try adding it.
        if candidate.suffix != ".dart":
            candidate_dart = candidate.with_suffix(".dart")
            if candidate_dart.exists():
                return candidate_dart
        return None

    # If import is like 'features/x/...' treat as lib-relative.
    candidate = root / "lib" / imp
    if candidate.exists():
        return candidate
    candidate2 = root / imp
    if candidate2.exists():
        return candidate2
    return None


def _parse_pubspec_dependencies(pubspec_text: str) -> dict[str, str]:
    # Lightweight parser (no PyYAML dependency). Good enough for common pubspec formats.
    deps: dict[str, str] = {}
    lines = pubspec_text.splitlines()

    def _indent(s: str) -> int:
        return len(s) - len(s.lstrip(" "))

    dep_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "dependencies:":
            dep_idx = i
            break
    if dep_idx is None:
        return deps

    base_indent = _indent(lines[dep_idx])
    i = dep_idx + 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        cur_indent = _indent(line)
        if cur_indent <= base_indent:
            break

        # Handle multi-line entries like:
        # flutter:
        #   sdk: flutter
        # We only care about top-level package keys under dependencies.
        m = re.match(r"^\s{1,}([a-zA-Z0-9_]+)\s*:\s*(.*)$", line)
        if m and cur_indent == base_indent + 2:
            name = m.group(1)
            rest = m.group(2).strip()
            if rest:
                # e.g. dio: ^5.3.3
                deps[name] = rest
            else:
                # multi-line mapping; skip children but record "sdk" if present
                j = i + 1
                nested_indent = None
                sdk_value = None
                while j < len(lines):
                    l2 = lines[j]
                    if not l2.strip() or l2.strip().startswith("#"):
                        j += 1
                        continue
                    ind2 = _indent(l2)
                    if ind2 <= cur_indent:
                        break
                    if nested_indent is None:
                        nested_indent = ind2
                    # sdk: flutter
                    m2 = re.match(r"^\s+sdk\s*:\s*(.+)\s*$", l2)
                    if m2:
                        sdk_value = m2.group(1).strip()
                    j += 1
                if sdk_value:
                    deps[name] = f"sdk:{sdk_value}"
                i = j
                continue
        i += 1
    return deps


@dataclass(frozen=True)
class Finding:
    code: str
    title: str
    file: str | None = None
    details: str | None = None
    suggestion: str | None = None
    severity: str = "warn"  # info|warn|error


def _score_from_findings(findings: list[Finding]) -> dict[str, float]:
    # Simple scoring heuristic: start at 10 and subtract weighted issues per category.
    weights = {"info": 0.15, "warn": 0.5, "error": 1.0}
    buckets: dict[str, float] = {
        "Structure": 10.0,
        "Layer Separation": 10.0,
        "Naming": 10.0,
        "Networking": 10.0,
        "State Management": 10.0,
        "Reusability": 10.0,
        "Scalability": 10.0,
        "Maintainability": 10.0,
    }
    mapping = {
        "STRUCT": "Structure",
        "DEPS": "Layer Separation",
        "NAMING": "Naming",
        "NET": "Networking",
        "STATE": "State Management",
        "REUSE": "Reusability",
        "SCALE": "Scalability",
        "MAINT": "Maintainability",
    }
    for f in findings:
        key = mapping.get(f.code.split("_", 1)[0])
        if not key:
            continue
        buckets[key] -= weights.get(f.severity, 0.5)
    for k in list(buckets.keys()):
        buckets[k] = max(0.0, min(10.0, buckets[k]))
    return buckets


def analyze(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    pubspec_path = root / "pubspec.yaml"
    if pubspec_path.exists():
        pubspec_text = _read_text(pubspec_path)
        deps = _parse_pubspec_dependencies(pubspec_text)
        if not deps:
            findings.append(
                Finding(
                    code="STRUCT_PUBSPEC_NO_DEPS",
                    title="pubspec.yaml has no dependencies block",
                    file=_rel(root, pubspec_path),
                    details="Couldn't find a 'dependencies:' section to validate the baseline stack.",
                    severity="warn",
                )
            )
        else:
            # Missing deps
            missing = [k for k in DEPENDENCIES_BASELINE.keys() if k not in deps]
            if missing:
                findings.append(
                    Finding(
                        code="STRUCT_DEPS_BASELINE_MISSING",
                        title="Missing baseline dependencies",
                        file=_rel(root, pubspec_path),
                        details=", ".join(missing[:20]) + (" ..." if len(missing) > 20 else ""),
                        suggestion="Add the missing packages (baseline) to pubspec.yaml dependencies.",
                        severity="warn",
                    )
                )

            # Version mismatches (ignore if dependency is path/git/hosted map)
            mismatched: list[str] = []
            for name, expected in DEPENDENCIES_BASELINE.items():
                actual = deps.get(name)
                if not actual:
                    continue
                # If it's a YAML map-like value (e.g. {path: ...}) we can't compare.
                if actual.startswith("{") or actual.startswith("sdk:") or actual.startswith("git:") or actual.startswith("path:"):
                    continue
                if actual != expected:
                    mismatched.append(f"{name} (expected {expected}, found {actual})")
            if mismatched:
                findings.append(
                    Finding(
                        code="STRUCT_DEPS_BASELINE_VERSION",
                        title="Baseline dependency version mismatches",
                        file=_rel(root, pubspec_path),
                        details="; ".join(mismatched[:10]) + (" ..." if len(mismatched) > 10 else ""),
                        suggestion="Align dependency versions with the agreed baseline (or document the reason for divergence).",
                        severity="info",
                    )
                )
    else:
        findings.append(
            Finding(
                code="STRUCT_PUBSPEC_MISSING",
                title="pubspec.yaml not found at root",
                details="Can't validate dependency baseline without pubspec.yaml at the provided root.",
                suggestion="Run the analyzer with --root pointing to the Flutter app root (where pubspec.yaml lives).",
                severity="warn",
            )
        )

    dart_files = _dart_files(root / "lib") if (root / "lib").exists() else _dart_files(root)
    if not dart_files:
        findings.append(
            Finding(
                code="STRUCT_NO_DART",
                title="No Dart files found",
                details="Couldn't find any .dart files under the provided root.",
                severity="error",
            )
        )
        return findings

    rels = [_rel(root, p) for p in dart_files]
    has_core = any(r.startswith("lib/core/") for r in rels)
    has_features = any(r.startswith("lib/features/") for r in rels)
    if not has_core:
        findings.append(
            Finding(
                code="STRUCT_CORE_MISSING",
                title="Missing lib/core structure",
                details="Expected shared app code to live under lib/core/.",
                suggestion="Create lib/core/{di,networking,routing,helpers,theming,widgets}/ and move shared code there.",
                severity="warn",
            )
        )
    if not has_features:
        findings.append(
            Finding(
                code="STRUCT_FEATURES_MISSING",
                title="Missing lib/features structure",
                details="Expected feature modules to live under lib/features/<feature>/...",
                suggestion="Create lib/features/<feature>/{data,logic,ui}/ and move feature code accordingly.",
                severity="warn",
            )
        )

    # Validate feature skeletons
    feature_dirs: set[str] = set()
    for r in rels:
        fn = _feature_name(r)
        if fn:
            feature_dirs.add(fn)
    for feature in sorted(feature_dirs):
        base = root / "lib" / "features" / feature
        expected = [
            base / "data",
            base / "logic",
            base / "ui",
        ]
        for e in expected:
            if not e.exists():
                findings.append(
                    Finding(
                        code="STRUCT_FEATURE_SKELETON",
                        title=f"Feature '{feature}' missing expected folder",
                        file=_rel(root, base),
                        details=f"Missing: {_rel(root, e)}",
                        suggestion=f"Add folder and organize code under {_rel(root, e)}",
                        severity="warn",
                    )
                )

    # File scanning
    resolved_layer: dict[str, str] = {}
    resolved_feature: dict[str, str | None] = {}
    file_text: dict[str, str] = {}
    file_lines: dict[str, int] = {}

    for p in dart_files:
        rp = _rel(root, p)
        t = _read_text(p)
        file_text[rp] = t
        file_lines[rp] = _count_lines(t)
        resolved_layer[rp] = _classify_layer(rp)
        resolved_feature[rp] = _feature_name(rp)

    # Naming checks
    for rp in rels:
        base = os.path.basename(rp)
        if re.search(r"[A-Z]", base):
            findings.append(
                Finding(
                    code="NAMING_CAMEL_FILE",
                    title="Non-snake_case file name",
                    file=rp,
                    details=f"File name contains uppercase letters: {base}",
                    suggestion="Rename file to snake_case (e.g., login_cubit.dart).",
                    severity="warn",
                )
            )
        if base.count("__") > 0:
            findings.append(
                Finding(
                    code="NAMING_DOUBLE_UNDERSCORE",
                    title="Suspicious file name (double underscores)",
                    file=rp,
                    details=base,
                    severity="info",
                )
            )

    # File size checks
    for rp, nlines in file_lines.items():
        kind = _file_kind(rp)
        if not kind:
            continue
        limit = DEFAULT_THRESHOLDS.get(kind)
        if limit and nlines > limit:
            findings.append(
                Finding(
                    code="MAINT_FILE_TOO_LARGE",
                    title=f"Large {kind} file",
                    file=rp,
                    details=f"{nlines} lines (threshold {limit})",
                    suggestion="Split into smaller widgets/classes; extract helpers; keep screens thin.",
                    severity="warn",
                )
            )

    # Dependency analysis
    layer_rank = {"ui": 3, "logic": 2, "data": 1}
    for rp, text in file_text.items():
        src_layer = resolved_layer.get(rp, "other")
        src_feature = resolved_feature.get(rp)
        file_path = root / rp
        for imp in _iter_imports(text):
            target = _resolve_import(root, file_path, imp)
            if not target:
                continue
            tp = _rel(root, target)
            dst_layer = resolved_layer.get(tp, _classify_layer(tp))
            dst_feature = resolved_feature.get(tp, _feature_name(tp))

            # core -> feature forbidden
            if src_layer == "core" and dst_layer in {"ui", "logic", "data", "feature-unknown"}:
                findings.append(
                    Finding(
                        code="DEPS_CORE_IMPORTS_FEATURE",
                        title="Core imports feature code",
                        file=rp,
                        details=f"Imports: {imp} -> {tp}",
                        suggestion="Invert dependency: move shared abstractions to core and feature implementations depend on them.",
                        severity="error",
                    )
                )

            # feature -> feature forbidden (direct)
            if src_feature and dst_feature and src_feature != dst_feature:
                findings.append(
                    Finding(
                        code="DEPS_CROSS_FEATURE_IMPORT",
                        title="Direct feature-to-feature dependency",
                        file=rp,
                        details=f"Feature '{src_feature}' imports '{dst_feature}' via {imp}",
                        suggestion="Extract shared code to lib/core (widgets/helpers/theming) or define contracts in core.",
                        severity="error",
                    )
                )

            # Layer ordering inside features
            if src_layer in layer_rank and dst_layer in layer_rank:
                if layer_rank[dst_layer] > layer_rank[src_layer]:
                    findings.append(
                        Finding(
                            code="DEPS_WRONG_DIRECTION",
                            title="Layer dependency violation",
                            file=rp,
                            details=f"{src_layer} imports {dst_layer}: {imp}",
                            suggestion="Depend only downward: ui -> logic -> data. Use interfaces if needed.",
                            severity="error",
                        )
                    )

            # Data layer importing UI anywhere (common smell even if outside feature)
            if src_layer == "data" and dst_layer == "ui":
                findings.append(
                    Finding(
                        code="DEPS_DATA_IMPORTS_UI",
                        title="Data layer imports UI",
                        file=rp,
                        details=f"Imports: {imp}",
                        severity="error",
                    )
                )

    # UI smells: setState / http urls
    for rp, text in file_text.items():
        layer = resolved_layer.get(rp, "other")
        if layer == "ui":
            if "setState(" in text:
                findings.append(
                    Finding(
                        code="STATE_SETSTATE_IN_UI",
                        title="setState usage inside feature UI",
                        file=rp,
                        details="Found setState(...) in a UI file. This can be OK for local UI state, but review for business logic leakage.",
                        suggestion="Prefer Cubit/Bloc for business state; keep setState for ephemeral UI-only state.",
                        severity="warn",
                    )
                )
            if "Dio(" in text or re.search(r"\\bhttp\\.(get|post|put|delete)\\b", text):
                findings.append(
                    Finding(
                        code="NET_API_CALL_IN_UI",
                        title="Potential API call in UI layer",
                        file=rp,
                        details="Found Dio(...) or http.* usage in a UI file.",
                        suggestion="Move networking to data layer (repos/data_sources) and call via cubit/usecase.",
                        severity="error",
                    )
                )

        # Hardcoded URLs anywhere
        for m in HTTP_RE.finditer(text):
            url = m.group(0)
            findings.append(
                Finding(
                    code="NET_HARDCODED_URL",
                    title="Hardcoded URL detected",
                    file=rp,
                    details=url,
                    suggestion="Move base URLs to a centralized config (core/networking) and environment flavors.",
                    severity="warn",
                )
            )

    # Routing smells: Navigator usage spread outside core/routing
    for rp, text in file_text.items():
        if "Navigator.push" in text or "Navigator.of(" in text:
            if not rp.startswith("lib/core/routing/"):
                findings.append(
                    Finding(
                        code="MAINT_SCATTERED_NAV",
                        title="Navigation logic outside core/routing",
                        file=rp,
                        details="Found Navigator.push*/Navigator.of(...) usage.",
                        suggestion="Centralize routing: define route names and navigation helpers in lib/core/routing/.",
                        severity="info",
                    )
                )

    # Networking smells: Dio usage outside core/networking or data layer
    for rp, text in file_text.items():
        if "Dio(" in text:
            if ("/core/networking/" not in rp.replace("\\", "/")) and ("/data/" not in rp.replace("\\", "/")):
                findings.append(
                    Finding(
                        code="NET_DIO_OUTSIDE_DATA",
                        title="Dio setup/usage outside data/core networking",
                        file=rp,
                        details="Found Dio(...) usage outside data layer or core/networking.",
                        suggestion="Keep Dio client + interceptors in core/networking and access it from repos/data_sources.",
                        severity="warn",
                    )
                )

    # Reusability hints: repeated hex colors / EdgeInsets patterns
    color_counts: Counter[str] = Counter()
    inset_counts: Counter[str] = Counter()
    for text in file_text.values():
        color_counts.update(COLOR_HEX_RE.findall(text))
        inset_counts.update(
            ["EdgeInsets." + m.group(1) + "(" + re.sub(r"\\s+", "", m.group(2)) + ")" for m in EDGEINSETS_RE.finditer(text)]
        )
    for color, cnt in color_counts.most_common(20):
        if cnt >= 6:
            findings.append(
                Finding(
                    code="REUSE_REPEATED_COLOR",
                    title="Repeated color literal",
                    details=f"{color} appears {cnt} times",
                    suggestion="Extract to core/theming (e.g., AppColors) and reuse.",
                    severity="info",
                )
            )
    for inset, cnt in inset_counts.most_common(20):
        if cnt >= 8:
            findings.append(
                Finding(
                    code="REUSE_REPEATED_INSETS",
                    title="Repeated EdgeInsets pattern",
                    details=f"{inset} appears {cnt} times",
                    suggestion="Extract to core/helpers or a spacing system in core/theming.",
                    severity="info",
                )
            )

    # Basic duplication (exact file hash) for small widgets/helpers
    hash_to_files: dict[str, list[str]] = defaultdict(list)
    for rp, text in file_text.items():
        if file_lines[rp] <= 250:
            h = hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
            hash_to_files[h].append(rp)
    for files in hash_to_files.values():
        if len(files) >= 3:
            findings.append(
                Finding(
                    code="REUSE_DUPLICATE_FILES",
                    title="Potential duplicated files (identical content)",
                    details="; ".join(sorted(files)[:10]) + (" ..." if len(files) > 10 else ""),
                    suggestion="Deduplicate: keep one implementation and move shared widget/helper to lib/core.",
                    severity="warn",
                )
            )

    return findings


def render_report(root: Path, findings: list[Finding]) -> str:
    scores = _score_from_findings(findings)
    overall = sum(scores.values()) / len(scores) if scores else 0.0

    def status_for(section: str) -> str:
        s = scores.get(section, 0.0)
        if s >= 8.5:
            return "✅ Good"
        if s >= 6.5:
            return "⚠️ Needs Work"
        return "❌ Issues Found"

    buckets: dict[str, list[Finding]] = defaultdict(list)
    for f in findings:
        buckets[f.code.split("_", 1)[0]].append(f)

    lines: list[str] = []
    lines.append("# Architecture Review Report")
    lines.append("")
    lines.append("## Overall Score")
    lines.append(f"{overall:.1f} / 10")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Section | Status |")
    lines.append("|---|---|")
    for section in [
        "Structure",
        "Layer Separation",
        "Naming",
        "Networking",
        "State Management",
        "Reusability",
        "Scalability",
        "Maintainability",
    ]:
        lines.append(f"| {section} | {status_for(section)} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    if not findings:
        lines.append("## Violations")
        lines.append("")
        lines.append("No issues detected by the current heuristics.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Violations & Findings")
    lines.append("")
    for idx, f in enumerate(findings, start=1):
        sev = {"info": "Info", "warn": "Warning", "error": "Error"}.get(f.severity, f.severity)
        lines.append(f"### {idx}. {f.title} ({sev})")
        lines.append("")
        if f.file:
            lines.append("File:")
            lines.append("```text")
            lines.append(f.file)
            lines.append("```")
            lines.append("")
        if f.details:
            lines.append("Problem:")
            lines.append("")
            lines.append(f"- {f.details}")
            lines.append("")
        if f.suggestion:
            lines.append("Suggested Fix:")
            lines.append("")
            lines.append(f"- {f.suggestion}")
            lines.append("")
        lines.append("---")
        lines.append("")

    # Refactor Plan
    high: list[str] = []
    med: list[str] = []
    low: list[str] = []
    for f in findings:
        if f.severity == "error":
            high.append(f.title + (f" ({f.file})" if f.file else ""))
        elif f.severity == "warn":
            med.append(f.title + (f" ({f.file})" if f.file else ""))
        else:
            low.append(f.title + (f" ({f.file})" if f.file else ""))

    def _cap(items: list[str], n: int = 12) -> list[str]:
        return items[:n] + (["..."] if len(items) > n else [])

    lines.append("## Refactor Plan")
    lines.append("")
    lines.append("### High Priority")
    lines.append("")
    if high:
        for it in _cap(high):
            lines.append(f"- {it}")
    else:
        lines.append("- (None detected)")
    lines.append("")
    lines.append("### Medium Priority")
    lines.append("")
    if med:
        for it in _cap(med):
            lines.append(f"- {it}")
    else:
        lines.append("- (None detected)")
    lines.append("")
    lines.append("### Low Priority")
    lines.append("")
    if low:
        for it in _cap(low):
            lines.append(f"- {it}")
    else:
        lines.append("- (None detected)")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This report is heuristic-based (static scan). Verify findings in context.")
    lines.append("- Tighten/relax thresholds and patterns in scripts/analyze_flutter_arch.py as needed.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Analyze Flutter/Dart repo for architecture compliance.")
    parser.add_argument("--root", default=".", help="Repo root (contains lib/).")
    parser.add_argument("--out", default="", help="Output markdown file path (default: stdout).")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    findings = analyze(root)
    report = render_report(root, findings)

    if args.out:
        out_path = Path(args.out).resolve()
        out_path.write_text(report, encoding="utf-8")
    else:
        sys.stdout.write(report)
        if not report.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

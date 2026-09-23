---
name: ios-security-audit
description: Audit iOS Swift applications for banking-grade mobile security risks and generate a clear PDF security audit report. Use when reviewing Swift source, Info.plist, entitlements, Podfile/Package.swift, or Xcode configuration for issues in sensitive storage, network hardening, auth controls, API safety, jailbreak detection, reverse engineering resistance, privacy permissions, and sensitive UI protection.
---

# iOS Security Audit

## Overview
Perform a structured security audit of an iOS project, assign severity to findings, calculate a Security Score out of 100, and produce a PDF report with actionable fixes and Swift code examples.

## Workflow

1. Collect scope and inventory.
2. Scan code and configuration for risks across the audit areas.
3. Classify findings by severity and impact.
4. Build a weighted security score out of 100.
5. Generate a Markdown report first, then export it to PDF.

## Step 1: Collect Scope
Identify and read:
- Swift source files (`*.swift`)
- `Info.plist`
- `*.entitlements`
- `Podfile`, `Package.swift`
- Build configuration and project settings when available

Prefer fast search patterns:
- `rg --files`
- `rg -n "UserDefaults|Keychain|kSecAttrAccessible|NSAppTransportSecurity|NSAllowsArbitraryLoads|http://|URLSessionDelegate|LocalAuthentication|LAContext|print\\(|os_log|isCaptured|UIScreen|jailbreak|cydia|canOpenURL|accessToken|apiKey|secret|password|Bearer"`

## Step 2: Audit Areas

### 1) Sensitive Data Storage
Flag:
- Tokens/passwords/PINs/user IDs in `UserDefaults`
- Plain-text local file storage of secrets
- Missing Keychain usage for sensitive values
- Weak keychain accessibility

Prefer:
- Keychain Services
- `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly`
- `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`

### 2) Network Security
Flag:
- `http://` endpoints
- ATS weakening (`NSAllowsArbitraryLoads = true`)
- Unsafe custom `URLSessionDelegate`
- Missing pinning for sensitive banking APIs

Prefer:
- HTTPS only
- ATS enabled by default
- Certificate/public key pinning for critical APIs

### 3) Authentication
Flag:
- Missing or weak `LocalAuthentication`
- Sensitive actions without step-up auth
- Insecure fallback flows

Prefer:
- Face ID / Touch ID for sensitive actions
- Re-authentication for transfers/payments/profile security changes

### 4) API Security
Flag:
- Hardcoded keys/tokens/secrets
- Logging bearer tokens or sensitive responses
- Missing timeout/retry boundaries
- Missing response validation/error handling

Prefer:
- No secret literals in source
- Redacted secure logging
- Explicit timeouts and strict validation

### 5) Jailbreak / Device Integrity
Flag:
- No jailbreak/tamper checks for high-risk flows
- No restrictions on compromised devices

Prefer:
- File/path checks, URL scheme checks, sandbox integrity checks
- Disable or reduce critical operations on compromised devices

### 6) Screenshot / Screen Recording Protection
Flag:
- Sensitive UI visible in app switcher/background
- No capture detection for sensitive screens

Prefer:
- Blur/hide sensitive content on background
- Handle `UIScreen.main.isCaptured` for high-risk views

### 7) Reverse Engineering Protection
Flag:
- Verbose debug logs in production paths
- Hardcoded sensitive strings
- Missing anti-tamper/obfuscation strategy documentation

Prefer:
- Strip or gate debug logging
- Move secrets to secure runtime retrieval

### 8) Permissions and Privacy
Flag:
- Unused permissions
- Missing/weak purpose strings
- Over-broad permission usage

Prefer:
- Least privilege
- Clear purpose descriptions aligned with real usage

## Severity Model
Use exactly one severity per finding:
- Critical
- High
- Medium
- Low
- Informational

Classify by exploitability, impact, and user harm (financial fraud/data theft risk weighted heavily).

## Security Score Model (0-100)
Start at `100`, subtract penalties:
- Critical: `-20` each
- High: `-10` each
- Medium: `-5` each
- Low: `-2` each
- Informational: `-0`

Clamp minimum at `0`.

Risk bands:
- `85-100`: Low Risk
- `70-84`: Medium Risk
- `50-69`: High Risk
- `0-49`: Critical Risk

Always include:
- `Security Score: X / 100`
- `Risk Level: <band>`
- 2-4 sentence score summary

## Output Requirements
Create report in Markdown first, then export to PDF.

Required sections in order:
1. Executive Summary
2. Security Score
3. Positive Findings
4. Critical Issues
5. Detailed Findings
6. Recommended Fixes
7. Swift Code Examples
8. Final Checklist

Use this finding template:

```md
### Finding Title

Severity: High

File:
`Path/To/File.swift`

Problem:
Explain the issue clearly.

Why it matters:
Explain the security risk.

Bad code:
```swift
...
```

Recommended fix:
```swift
...
```

Status:
Needs improvement
```

## Final Checklist Template

```md
- [ ] No sensitive data in UserDefaults
- [ ] Keychain used for tokens and secrets
- [ ] ATS enabled
- [ ] HTTPS enforced
- [ ] Certificate pinning added
- [ ] No hardcoded secrets
- [ ] No sensitive logs
- [ ] Jailbreak detection implemented
- [ ] Screenshot/screen recording protection added
- [ ] LocalAuthentication used for sensitive actions
- [ ] Dependencies reviewed
- [ ] Production build has no debug symbols
```

## Report Generation Notes
- Quote short, relevant code snippets only.
- Prefer concrete file paths and exact evidence.
- If evidence is absent, state that explicitly as a gap or unknown.
- Keep recommendations implementation-ready for Swift/iOS teams.
- If PDF tooling is unavailable, provide final Markdown and note the PDF conversion command to run.

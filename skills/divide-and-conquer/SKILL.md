---
name: divide-and-conquer
description: >
  Use this skill for any engineering or problem-solving task that involves complexity,
  ambiguity, or multiple moving parts. Triggers include: debugging hard bugs, designing
  system architecture, refactoring large codebases, implementing multi-step features,
  planning sprints or technical tasks, or any time the user says "I don't know where to
  start" or "this is too complex". Also use when reviewing code, designing APIs, breaking
  down user stories, or solving algorithmic challenges. ALWAYS use this skill before
  jumping to a solution — decompose first, solve second. Works across iOS (UIKit/SwiftUI),
  Android (Kotlin/Jetpack Compose), Flutter, and general software engineering tasks.
---

# Divide & Conquer Skill

You are an expert software engineer using a strict **Divide & Conquer** workflow.
Never jump to a final solution. Always decompose the problem first.

---

## CORE PHILOSOPHY

Every complex problem is just a collection of small, solvable problems.
Break it apart → solve each piece → combine into the final solution.

---

## MANDATORY PROCESS

### 1) UNDERSTAND
- Restate the problem clearly in your own words
- Define:
  - **Inputs**: What is given?
  - **Outputs**: What is expected?
  - **Constraints**: Platform, performance, existing code, deadlines?
- If anything is unclear → ask before proceeding

---

### 2) DECOMPOSE *(Critical Step)*
- Split the problem into **subproblems**
- Each subproblem must be:
  - ✅ Small (can be solved in isolation)
  - ✅ Testable (has a clear pass/fail)
  - ✅ Independent (if possible)
- Use a numbered list — visualize the breakdown clearly
- **Do NOT write any code yet**

---

### 3) PLAN
- Order the subproblems logically (dependencies first)
- Define how each subproblem connects to the next
- Flag any risks or unknowns upfront

---

### 4) TEST DESIGN *(TDD-first)*
For each subproblem, define:
- ✅ Normal case (happy path)
- ⚠️ Edge case (empty, nil, zero, boundary)
- ❌ Failure case (what should break gracefully)

> If subproblem output is obvious and trivial, you may skip formal test design for it.

---

### 5) SOLVE SUBPROBLEMS
For **each** subproblem:
1. Briefly explain your approach (1–2 lines)
2. Write clean, minimal code
3. Confirm it satisfies the test cases defined above
4. Keep it modular — no cross-dependencies between subproblems unless planned

---

### 6) COMBINE
- Integrate all subproblem solutions
- Check interfaces match (types, naming, data flow)
- Ensure the combined solution handles all test cases end-to-end

---

### 7) REVIEW
- ✅ Does the solution solve the original problem?
- ✅ Is the code clean and readable?
- ⚡ Any performance concerns?
- ⚠️ Any risks, edge cases not covered, or technical debt introduced?
- 📌 Any follow-up tasks needed?

---

## RULES

| Rule | Description |
|------|-------------|
| 🚫 No jumping | NEVER write the final solution before decomposing |
| 🧩 Modular always | Each subproblem solution must stand alone |
| 🔍 Clarity first | Prefer readable code over clever one-liners |
| ❓ Unknown? Say it | If unsure about something → mark it `UNKNOWN` and ask |
| 🔁 Iterate | If a subproblem is too big → decompose it further |

---

## PLATFORM NOTES

When working on mobile:
- **iOS (UIKit/SwiftUI)**: Decompose by: ViewController lifecycle / View / ViewModel / Service / Model
- **Android (Kotlin/Compose)**: Decompose by: Screen / ViewModel / Repository / DataSource
- **Flutter**: Decompose by: Widget / BLoC or Provider / Service / Model

When working on algorithms:
- Decompose by: Input validation → Core logic → Output formatting → Edge cases

---

## OUTPUT FORMAT

Always structure your response like this:

```
## UNDERSTAND
...

## DECOMPOSE
1. Subproblem A
2. Subproblem B
3. ...

## PLAN
...

## TEST DESIGN
...

## SOLVE
### Subproblem 1: ...
### Subproblem 2: ...

## COMBINE
...

## REVIEW
...
```

---

## EXAMPLE TRIGGER PHRASES

- "فيه bug مش عارف أحله"
- "محتاج أعمل feature معقدة"
- "مش عارف أبدأ منين"
- "refactor الكود ده"
- "ازاي أعمل X في iOS / Android"
- "I need to design this feature"
- "This is getting complicated"

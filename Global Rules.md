# Cline Global Rules

## 1. General Behavior

- Do not perform large refactors unless explicitly requested.
- Prefer minimal, targeted changes that solve the current request.
- Preserve existing style, patterns, and architecture unless the user explicitly asks to change them.
- Never introduce new dependencies, frameworks, or build tooling without explicit permission.
- Before changing any file, infer the intent from context; if unclear, default to the smallest safe change.

## 2. Code Changes

- Keep changes **small, cohesive, and well-scoped**.
- Do not rename files, modules, or classes unless the user explicitly requests it.
- Do not move files across folders unless the user explicitly requests it.
- Maintain existing code style (indentation, quotes, naming, etc.).
- When adding new code, place it near related code instead of creating scattered snippets.

## 3. Safety & Stability

- Assume the project is already fragile; do not break existing working behavior just to "clean up" code.
- If you must change behavior to implement a feature, keep the change as isolated as possible.
- Avoid speculative "improvements" that are not directly tied to the user’s request.

## 4. Communication

- When responding, summarize:
  - Files you will touch
  - The type of change in each file
- For non-trivial changes, include a short “What changed / Why” explanation.
- Do not generate long explanations that repeat obvious facts from the code.

## 5. Testing & Verification

- If there are existing scripts (e.g. `npm test`, `pytest`, etc.), mention which command should be run to verify changes, but do not invent tests that don’t fit the current request.
- Do not add heavy test frameworks or large test suites unless explicitly asked.

## 6. Limits

- No automatic “modernization” passes (e.g., converting everything to hooks, TypeScript, async/await) unless explicitly requested.
- No style or lint config changes (ESLint, Prettier, Black, etc.) without explicit instruction.

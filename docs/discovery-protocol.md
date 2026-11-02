# Bounded unseeded-policy feasibility probe

Predeclared before invocation `unseeded-policy-002`, 2 November 2026.

**Question:** Does a model-generated verification policy, written from the intended interface and task requirements without a supplied buggy policy or failure feedback, exhibit a verification failure on the existing development family?

This is an unseeded **policy** probe on **authored fixtures**. It is not a field study, a search through real coding-agent production failures, or a held-out audit. Calling the result a naturally occurring failure in a real repository would overstate it.

Use one existing-allowance Codex invocation, exact model `gpt-6.1-sol`, low reasoning, timeout 120 seconds, no tools, no API-key fallback. Request exactly one small pure `choose_action` program. Provide the interface and the task's completion requirements; do not provide the original always-complete policy, any failed trace, the earlier successful repairs, or transformation names.

After generation, freeze the program unchanged and evaluate all seven current development cases, including the unchanged control, through the isolated worker. Preserve every outcome. An invalid program or runtime error is an invalid/failed generation, not a freshness bug. A semantic failure requires functional correctness plus an unsupported completion claim or inability to complete under the bounded interface, with its full trace retained.

Do not resample if the program succeeds. A fully successful policy is evidence that these simple, explicit-provenance cases may be too easy for the proposed selection study. If a valid policy fails, diagnose it before deciding whether the last remaining invocation should attempt repair. No audit cases are created or opened in this probe.

Stop after this one generation. Keep the remaining invocation available rather than spend it on a larger sweep without a new predeclared question.

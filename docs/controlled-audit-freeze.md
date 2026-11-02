# Controlled pilot external freeze

The C1 audit plan was frozen before executing its task templates.

- Plan: `evidence/controlled-transfer-012/plan.json`.
- Canonical plan hash: `fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3`.
- Scope: one authored source pool, two unchanged generated repairs, three pre-existing matched selector decisions, nine new cases and one nonselectable authored reference.
- Allowance: 36 local trials, zero new model calls, no automatic retries.
- Before execution: all 60 development traces replayed and their selector decisions recomputed. No audit trial directory or outcome exists.
- Commit this file, plan, pool and source snapshots before opening outcomes. Git history records the ordering. This provides procedural separation, not author blinding or protection against complete history replacement.

Use this hash with the runner's `--expected-hash` argument. No subsequent outcome can authorize changing this plan or replacing a candidate. The original native-agent main study remains unperformed.

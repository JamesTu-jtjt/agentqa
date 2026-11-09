# AgentQA contributor instructions

- This directory is an independent Git repository. Run project and Git commands here; preserve neighboring projects.
- Use `james-tu/` for new branches unless requested otherwise.
- Read `README.md`, `docs/research-scope.md`, and relevant study protocols before changes.
- Preserve frozen plans, source snapshots, evidence, hashes, and failed attempts. New experiments use new output directories and never overwrite prior results.
- Distinguish authored fault injection, generated policies, and naturally observed failures. Do not infer selector benefits or long-run improvements from the bounded studies.
- Keep test and audit data outside candidate-visible workspaces. Generated programs run in the isolated worker; the local evaluator is for trusted authored code.
- Run `.venv/bin/python -m pytest` and saved-evidence verification after relevant changes. No new model calls are part of routine reproduction; the historical three-call allowance is exhausted.
- Preserve third-party licenses and attribution. Exclude credentials, local planning notes, and runtime directories from commits.
- Public repository: `https://github.com/JamesTu-jtjt/agentqa`. Repository maintenance does not authorize upstream messages or new experiments.

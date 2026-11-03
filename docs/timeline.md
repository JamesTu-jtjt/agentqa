# Project timeline

**Completed follow-up, 2 November:** N1/N2 were frozen before execution, completed native/standard-helper comparisons, replayed durable evidence and updated the report/private repository. The clean noneditable install passed 145 tests with three optional Docker skips. This bounded extension used zero new inference. Existing milestone estimates below remain historical; the model-repair main study is still deferred.

Planning date and implementation kickoff: 2 November 2026. Implementation owner: Codex. Research/resource owner: James. The first session delivered the local measurement core, family controls, container worker, and a one-invocation Codex feasibility pilot. See `status.md` for actual completion; the table below remains the original baseline estimate.

**Baseline: eight working days from implementation kickoff, plus up to two contingency days.** These are planning blocks, not a promise of eight days of continuous agent activity. No deadline has been supplied and nothing is scheduled automatically. Calendar dates will be assigned once kickoff and any deadline are known. Faster completion is appropriate when a milestone is satisfied; a date never overrides an unresolved validity issue.

The minimum submission is the proof of concept, comparative evidence, report, reproducible bundle, and a short replay. Long-run evolution, new failure classes, extra languages, a dashboard, and extensive model sweeps are outside the baseline.

## Milestones and completion checks

| Milestone | Target | Codex's work | Completion evidence | Dependencies |
| --- | --- | --- | --- | --- |
| M0: Planning and separation | Complete, 2 Nov | Preserve proposal; initialize independent repo; write timeline, TODOs, and runbook. | Repository boundary checks and planning documents. | None. |
| M1: Freeze development specification | Day 1 | Specify footprint semantics, task success, event schema, family definitions, novelty boundary, and planned comparisons. Inspect the relevant upstream interfaces and licenses. | Development protocol and a worked source/contrastive pair; a bounded implementation design. | M0. |
| M2: Trustworthy local measurement | Day 2 | Implement fixtures, an external recorder, footprint calculation, completion oracle, sandbox runner, and reference controllers. | Offline tests detect stale evidence and accept fresh evidence; a valid reference completes the task. | M1. |
| M3: Test-family construction | Day 3 | Implement transformations, applicability validation, generic baseline, deterministic fixtures, and replay. | Validity suite; invalid cases rejected; a documented narrow repair is distinguished from a robust reference. | M2. |
| M4: Agent and evolution integration | Day 4 | Add the agent/model interface, bounded editable module, ShinkaEvolve adapter, trial ledger, and cost limits. | Offline adapter tests and mocked end-to-end execution; upstream revision recorded. | M2–M3; provider selection needed only for a live check. |
| M5: Feasibility and cost pilot | Day 5 | Run a bounded live pilot; investigate natural source failures; verify candidate variability and measure full episode cost. | Pilot memo, natural/seeded labels, projected total cost, finalized experiment scope. | M4; model access and spending limit resolved. |
| M6: Freeze and selection evaluation | Day 6 | Prepare sealed audit; freeze protocol and analysis; generate/freeze common candidate pools; run the three selectors and shared regression checks. | Freeze manifest, all candidate outcomes, selected IDs, audited run accounting. | M5; valid sources and affordable experiment size. |
| M7: Independent audit and analysis | Day 7 | Audit every frozen candidate and references; compute paired comparisons, costs, and case studies. | Reproducible tables/plots, audit outcomes, explicit exclusions and limitations. | M6; selection decisions recorded before audit outcomes are available. |
| M8: Submission package | Day 8 | Write report; package code/data; produce replay; verify reproduction from a clean environment. | Report, runnable artifact, reproduction manifest, replay, and completed delivery checklist. | M7. |

Preparation of report background and reproduction documentation can happen alongside M2–M6. Analysis code can be developed using synthetic outcomes before M6. Research conclusions wait for M7. Milestone order does not imply spawning additional agents.

## Decision points

**After M2 — Is the measurement correct?** Stop dependent experiments if the recorder accepts invented results, the relevant footprint is ambiguous, or a valid reference cannot complete a scenario. Fix the environment first. Treat a provenance mismatch as a measurement defect until explained.

**After M3 — Are the families valid and useful?** The demonstration must include applicable transformations and controls, not just cases that make agents fail. Always-rerun can be a legitimate repair; refusal is not successful task completion. This milestone uses labeled test doubles and cannot establish empirical novelty.

**After M5 — Is the scientific comparison feasible?** Use a predeclared pilot cap. If natural failures are sparse, document the search and either narrow to the observed cases or adopt a separately labeled controlled study. If candidate repairs lack diversity, make one bounded development revision within the pilot budget, record it, and refreeze. Do not search indefinitely for a favorable result.

**Before M7 — Is the audit still held out?** Confirm candidate and selector hashes, audit manifest, comparison budgets, retry policy, and prewritten analysis. If development has used audit outcomes, those cases become development data; construct a replacement audit or report an explicitly exploratory result.

**After M7 — What do the results support?** Report negative or inconclusive comparisons as such. New fixes or experiments after seeing the audit require a versioned exploratory analysis; they do not silently replace the primary result.

## Contingencies and schedule changes

| Condition | Response | Schedule effect |
| --- | --- | --- |
| Provider or budget unresolved | Finish local measurement, mocked integration, report background, and analysis templates. Leave live-run tasks pending. | Days 5–8 shift; time does not imply spending authorization. |
| ShinkaEvolve integration takes longer | Isolate adapter work from the evaluation core; use explicit mocked candidates for local development only. | Use one contingency day. Any change to the promised live integration must be recorded as a scope revision. |
| Natural failures remain sparse within pilot cap | Label and separate controlled failures; narrow claims. | Use up to one contingency day for diagnosis, not an open-ended search. |
| Experiment exceeds projected budget | Reduce candidate breadth/source pools before the final freeze; retain all three baselines and a separate audit. Report lower power. | Reduce scope rather than quietly reducing the rigor of one method. |
| Infrastructure failure during execution | Preserve attempt; retry only under the frozen infrastructure-retry rule. | Resume from the ledger without duplicating completed paid work. |
| Hypothesis unsupported | Complete the same report and reproducibility deliverables with negative findings. | No automatic extension to chase positive results. |

If a shorter deadline is supplied, prioritize M1–M4 plus a small, explicitly exploratory M5–M8 comparison. A polished offline demonstration alone must not be described as evidence that the selector improves real agent repair.

## Progress cadence

**90% scope amendment:** After the exhausted three-call pilot failed to yield a discriminating generated pool, C1 prospectively froze a small controlled transfer audit using unchanged cached policies and previously recorded selection decisions. The complete 36-trial audit is reported separately in `docs/checkpoint-090.md`; it does not satisfy the original native-agent M5–M7 study. Final delivery can close this explicitly inconclusive pilot without further inference. Broader native-agent claims remain deferred rather than silently counted complete.

At each active work session, Codex records the current milestone, completed TODO IDs and evidence, unresolved issues, spend so far, and the next executable step in `status.md`. Progress updates occur during active work; this plan does not create a reminder or background automation.

## Final delivery

James requested completion, then specified a native Google Doc like Neuroevolution instead of a PDF. The [final report](https://docs.google.com/document/d/1PWLTiMZQauiNg97_Um4I8RGOWvUUI98Og9RCj9XRrBU/edit?usp=drivesdk), local source, native table/figure readback, integrated replay, evidence and private-repository handover complete the bounded controlled pilot. No PDF is a final deliverable. The original native-agent main study remains separately unperformed; no additional inference allowance was used.

## Submission revision — 2 November 2026

At James’s request, the main report now centers on native evaluation acceptance and minimal defenses. The nondiscriminating selector pilot is a compact inconclusive study. Research ownership now explicitly credits James with overall direction, system design, experimental exploration and refinement; Codex assistance remains disclosed. Earlier full native/C1 reports are archived. No new experimental inference or audit was run; all saved evidence replays and the existing test suite passes. Main tab: https://docs.google.com/document/d/1PWLTiMZQauiNg97_Um4I8RGOWvUUI98Og9RCj9XRrBU/edit?tab=t.8naog6er2au7

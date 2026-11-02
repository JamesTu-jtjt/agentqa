# Current status and decisions

Updated: 2 November 2026.

**Progress:** Approximately **80%** of expected implementation/delivery effort; stopped at James's requested checkpoint after private publication verification. See `docs/checkpoint-080.md`.

**Milestone:** Core/pilot, grounded source, broader publication qualification, pre-audit analysis, recorded replay and clean prototype reproduction are delivered. Model-agent candidate diversity, final study sizing/freeze, matched selection, independent audit and final scientific delivery remain incomplete.

**Implementation owner:** Codex.

**Research/resource owner:** James.

**Live usage:** Three Codex subscription invocations; 27,232 input / 2,458 output tokens reported. Dollar cost unavailable.

**Allowance:** Three total persisted invocations, serial, at most 120 seconds each; **zero remain**.

**Implementation / experiments:** Development comparison remains inconclusive. Existing upstream scheduler behavior reproduced under authored failure/reuse conditions. Independent audit and naturally observed model-agent failures remain outstanding.

## Completed

- Preserved the research proposal at `proposal.md`.
- Initialized an independent Git repository at `/Users/james.tu/workspace/Interviews/Sakana/AgentQA` on `james-tu/agentqa`.
- Added README, agent instructions, timeline, TODOs, and execution runbook.
- Added a parent ignore rule and navigation links. Neuroevolution files and artifacts were not edited.
- Verified document links, distinct Git roots, initial branch, and the parent ignore rule during planning closeout.

The original M0 milestone involved no implementation or experiments. At the first implementation checkpoint (superseded by checkpoint 2 below), work completed included:

- **S11, S13:** executable development protocol and worked invalidation/unchanged controls in `docs/protocol.md`.
- **E20–E25:** installable standard-library core, trusted external records, fingerprints, actual test execution, functional/freshness oracle, trace integrity/replay, and meaningful boundary tests. A clean wheel install ran a verification smoke successfully.
- **F30–F35:** seven validated family cases, shared generic transformations, and authored narrow/robust/refusing controls. These use authored compaction/evidence presentations, not a real summarizer.
- **A46:** resource choice resolved through James's Codex login, exact `gpt-6.1-sol`, and a small operational invocation allowance. No API-key fallback.
- **B50:** one source-conditioned generation invocation produced two actual policy repairs; each passed seven development cases in Docker (14/14 verified). This is feasibility evidence from an authored source failure, not a natural-failure or selector result.
- Partial **A40–A45:** replaceable policy interface; Docker execution primitive; Codex backend; transactional budget and invocation ledgers; matched-slot selection rule. The full agent/evolution bridge, candidate registry, suite scheduler, and final split freeze remain incomplete.
- Reproducible outcome and design figures in `report/figures/`, with PNG/SVG/PDF and a generation manifest. Every plotted authored-control trace was replayed before plotting.

Initial checkpoint verification: 61 offline tests and the Docker checks passed. See `docs/pilot-001.md` for that milestone.

Initial checkpoint checks: all **49** recorded trials replayed with the expected manifest hashes and matching verdicts; documentation links resolved; the persistent ledger contains exactly one completed generation invocation; no AgentQA worker containers remained.

### Checkpoint 2

- **S10/S12:** methods reading and candidate/split specification documented in `docs/reading-notes.md` and `docs/candidate-split-spec.md`; the Nature version-of-record main methods were accessed through PMC.
- **A42–A45:** actual pinned ShinkaEvolve scheduler/evaluator check, immutable registry/frozen pool, matched suite scheduling, durable trial IDs, replay-validated resume, and shared selection/regression rule implemented. The full evolution loop and broader editable coding harness have not run.
- **B53:** feasibility assessment completed: the current generated repairs are uniformly successful, so this pool does not distinguish selectors.
- **60 development trials:** all three selectors chose `repair-00`; both repairs scored 6/6 on every selection suite and 2/2 common controls. No selection advantage established. Resume reused every completed trial without executing candidates.
- **One unseeded policy generation:** original attempts yielded four verified and three worker-timeout/infrastructure-inconclusive trials. No semantic bug confirmed. A linked diagnostic rerun of the unchanged policy completed 7/7 after startup/execution timing was separated. Original attempts remain preserved.
- Added measured comparison/timing figures, a hashed source snapshot, and isolated Shinka dependency lock. Interpretation and artifact links: `docs/checkpoint-002.md`.
- Latest verification: **68 offline tests passed**, three opt-in Docker cases skipped; the Docker file separately passed **7 tests**. All **125 recorded trial traces** replayed with expected hashes and verdicts. Two completed Codex invocations are in the persistent ledger.

### 50% checkpoint

- **S14, A40, A41:** finalized the three-call pilot allocation and added the bounded editable coding workflow. Generated controllers and generated task modules run in separate Docker workers. Host-owned files, receipts and expected answers remain outside the editable boundary. The replaceable controller supports memory, structured actions, reset, handoff and actual source edits.
- **18 new workflow trials:** authored reference 6/6; authored stale control 4/6, with the two expected stale-evidence failures; unseeded GPT-6.1 Sol generated controller 6/6. There were 152 worker invocations, 109.13 seconds measured worker time, no infrastructure-inconclusive cases and confirmed cleanup throughout.
- The generated controller reran after configuration changes and restored the exact tested source in the comment-change case. Both are valid under the existing contract. This is program generation followed by deterministic tool decisions, not a live LLM inference at each step or a native Sakana agent run.
- **Research feasibility remains inconclusive:** no natural semantic source failure or discriminating generated pool was found. The independent audit remains unopened. No selector advantage is demonstrated.
- **Verification:** 86 offline tests passed, three opt-in Docker cases skipped; the Docker file separately passed seven tests. All 143 trial traces replay with expected tips and verdicts. New program/case/plan/source and worker-result hashes checked. Figures were rendered and visually inspected.
- Full evidence, limits and progress estimate: `docs/checkpoint-050.md`. Local accounting/replay export: `evidence/checkpoint-050.json`.

### 70% checkpoint

- **B55:** six predeclared diagnostic cases through the unchanged real Shinka scheduler reproduced three stale/mixed attributions. A failed changed evaluation with code 7, a zero-exit nonpublisher and a partial publisher could expose earlier success from a reused output directory. Fresh-directory failure and complete-publication controls passed. This is an existing harness/API behavior under authored conditions, not an observed model reasoning error or a prevalence estimate.
- **B56:** added `bundles.py`, fifteen offline boundary tests and four actual adapter checks. Fresh attempt directories and host-bound request/execution/artifact receipts reject incomplete evidence. The first four checks remain separately preserved after launch-identity hardening.
- **B57:** implemented pre-audit analysis with eleven tests and a synthetic CLI example. It requires complete matched grids, frozen decisions and source-pool pairing; missing infrastructure and unknown cost cannot silently become failure/zero. No real audit was opened; the final freeze remains pending.
- New source diagnosis, license/attribution, measured figure, analysis protocol and working report are in the repository. Closer literature narrows the novelty claim to valid mechanism-directed repair selection, which still needs empirical evidence.
- **Verification:** 112 offline tests passed, three opt-in Docker cases skipped. All 143 old coding traces and eight new bundle receipts replay; six source diagnostic records and source/artifact hashes validate. Synthetic CLI output matches expectation. No new model calls; allowance remains exhausted.
- Assessment, scope and evidence: `docs/checkpoint-070.md`; verification/accounting export: `evidence/checkpoint-070.json`.

### 80% checkpoint

- **B58:** twenty fixed authored publication cases matched all contracts, with ten invariant renamed-layout pairs. Both valid negative results remained valid. No case was dropped or retried. These are development checks, not independent source pools or a model-agent audit.
- **D81–D84, current prototype:** portable evidence verifier, deterministic scanned archive builder, self-contained HTML replay and reproduction instructions delivered. A clean noneditable wheel install passed 124 tests (three opt-in Docker cases skipped), replayed 143 coding traces and 28 publication receipts, regenerated matching analysis and rebuilt byte-identical HTML. Four replay tabs and desktop rendering were checked; the temporary server was stopped.
- James explicitly authorized private GitHub publication. Account `JamesTu-jtjt` was verified; `JamesTu-jtjt/agentqa` was created and confirmed **PRIVATE before uploading files**. Post-push confirmation is in `evidence/github-publication-080.json`. Only project source/documents/selected evidence are uploaded; credentials, environments, transient runs, vendor checkout and Neuroevolution are excluded.
- No new model calls; lifetime allowance remains 3/3 consumed. Main generated-pool diversity, final freeze, selection and independent audit remain open. Earlier unfavorable/inconclusive results are preserved.
- Evidence: `docs/checkpoint-080.md`, `evidence/checkpoint-080.json`, `evidence/clean-reproduction-080.json`, `docs/reproduction.md`.

The authorized GitHub destination is private. No public release, collaborator invitation, upstream issue/PR or submission is implied. Local fixture/publication adapters execute only authored evaluators; generated code remains in Docker. No background experiment or automation continues.

## Decisions

| ID | Decision | Rationale |
| --- | --- | --- |
| DEC-001 | Separate local repository inside the existing writable workspace; no shared Task 1 history or submodule. | Meets repository separation while preserving the existing proposal path and workspace access. |
| DEC-002 | Eight relative working days plus up to two contingency days. | No external deadline or implementation kickoff date has been provided. Milestone checks govern progression. |
| DEC-003 | Initial mechanism is stale verification evidence. | Provides explicit provenance and an executable oracle for testing repair generalization. |
| DEC-004 | Fixed candidate pools, three matched selectors, and independent audit. | Isolates selection value from candidate-generation differences. |
| DEC-005 | Implement offline measurement before paid experiments. | Validates the apparatus and makes budget estimation possible. |
| DEC-006 | The single implementer is not blind to audit design. | Preserve procedural separation and acknowledge the limitation rather than claim independent human authorship. |
| DEC-007 | Content identity, including declared test/config inputs and runtime, governs verification freshness. | Exact restoration can reuse evidence in the fixed deterministic fixture; unrelated edits do not invalidate it. |
| DEC-008 | Use saved Codex account authentication with three total invocations and a 120-second per-invocation runtime bound. | Implements James's request to use Codex and keep usage low; subscription dollars cannot be measured here. |
| DEC-009 | Keep the pilot's uniformly successful repairs as an inconclusive selection case. | The two generated policies behave identically on current fixtures; do not manufacture overfitting or claim selector benefit. |
| DEC-010 | Separate container startup from candidate execution timeout, preserving original failed attempts. | Engine latency is not evidence of a semantic agent defect. |
| DEC-011 | Keep development comparison distinct from independent audit. | Repeated pure-policy slots and previously inspected templates cannot establish held-out repair transfer. |
| DEC-012 | Preserve the inconclusive stateful probe and stop at the requested 50% checkpoint. | A uniformly successful generated controller does not justify a larger search or a selector-benefit claim. The three-call pilot allowance is exhausted. |
| DEC-013 | On resumption, qualify an upstream evaluator boundary using local fault/reuse scenarios without more inference. | Supplies a concrete existing-code source while preserving the distinction between authored interventions and naturally observed model behavior. |
| DEC-014 | Keep result-publication attribution separate from the coding completion endpoint. | A valid negative evaluation is not invalid evidence; a controlled scheduler qualification is not an agent-repair selector study. |
| DEC-015 | Publish the reviewed prototype to James's private GitHub repository after explicit authorization. | Verify owner/privacy before upload; preserve project separation and exclude credentials/runtime/dependency directories. |
| DEC-016 | Complete prototype packaging at 80% without implying that the main study succeeded. | Reproduction/replay are concrete deliverables; native candidate diversity, final audit and research conclusions remain open. |

The proposal remains the research rationale. These documents operationalize it; they do not claim that proposed APIs, failure frequencies, or improvements have been verified.

## Pending inputs and when they matter

| Input | Current assumption | Needed by |
| --- | --- | --- |
| Deadline | Unspecified; implementation kicked off 2 Nov. | Final delivery scheduling. |
| Model/provider access | Resolved: Codex CLI saved ChatGPT login, `gpt-6.1-sol`. | First live check completed. |
| Pilot allowance | Resolved: low-usage three-invocation envelope; all three consumed. | Any new inference needs an explicit revised allowance; do not reset the ledger. |
| Large main study | Illustrative 1,572+ episodes remain an estimate, not the small pilot's execution allowance. | Reassess scope after natural-failure feasibility and candidate diversity checks. |
| Remote repository / publication destination | Resolved: authorized private `JamesTu-jtjt/agentqa`. | Keep private; no collaborator or public-release authorization. |
| Additional human review | No reviewer assigned. | Record actual review method during source-diagnosis validation; never imply review occurred. |

The requested 80% checkpoint is reached. No background work or automation is running. Preserve all outcomes and reuse the resolved model/access choice if James resumes; the inference allowance remains exhausted.

## Next action

When James resumes: use the grounded source to resolve **B51/B52/B54** and qualify a useful source-conditioned generated pool. Prepare a concrete small allowance before new inference, then freeze the final source/audit templates and protocol, complete selection, and only then open audit outcomes. An explicitly controlled/inconclusive report is an alternative scope decision. Do not substitute authored adapter tests for model-repair transfer, or count infrastructure timeouts as semantic failures. Broader native agent integration/evolution remains unperformed.

## Session log

| Date | Milestone / work | Evidence | Next |
| --- | --- | --- | --- |
| 2026-11-02 | M0: plan and repository setup | `README.md`, `AGENTS.md`, `docs/timeline.md`, `docs/todos.md`, `docs/execution.md`; repository/link checks | M1: S10–S13 |
| 2026-11-02 | First implementation session: measurement, families, controls, Docker worker, selection/ledger primitives, and Codex feasibility pilot | `docs/protocol.md`, `docs/upstream-review.md`, `docs/pilot-001.md`, tests, `evidence/`, `report/figures/` | Remaining M1/M4 work and natural-failure feasibility |
| 2026-11-02 | Checkpoint 2: real Shinka bridge, registry, matched runner, 60-trial comparison, unseeded probe and linked worker diagnosis | `docs/checkpoint-002.md`, `evidence/development-comparison-001/`, `evidence/unseeded-policy-002/`, `evidence/unseeded-worker-recheck-003/`, figures | Stateful coding-agent workflow and semantic-failure discovery |
| 2026-11-02 | Requested 50% checkpoint: stateful editable workflow, 12 real control trials and six generated-controller trials; final pilot call consumed | `docs/checkpoint-050.md`, `docs/workflow-protocol.md`, `evidence/workflow-controls-004/`, `evidence/stateful-controller-005/`, `report/figures/workflow-003/` | Stop here; on resumption, realistically grounded sources and final scope |
| 2026-11-02 | Requested 70% checkpoint: grounded upstream source, tested publication adapter, pre-audit analysis and working evidence report; no inference | `docs/checkpoint-070.md`, `evidence/upstream-source-006/`, `evidence/bound-shinka-007/`, `evidence/bound-shinka-008/`, `evidence/preaudit-analysis-010/`, `report/figures/upstream-004/` | Stop here; on resumption, generated candidate diversity and feasible final study |
| 2026-11-02 | Requested 80% checkpoint and private publication: twenty broader cases, portable verifier, replay, scanned archive and clean wheel/export check | `docs/checkpoint-080.md`, `evidence/publication-qualification-011/`, `evidence/clean-reproduction-080.json`, `report/demo/`, private GitHub repository | Stop after publication confirmation; main research gates remain open |

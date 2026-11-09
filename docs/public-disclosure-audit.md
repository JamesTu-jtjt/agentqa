# Public disclosure audit

Reviewed 9 November 2026. The repository is public at `JamesTu-jtjt/agentqa`.

## Review scope

The review covered tracked source, documentation, selected experimental artifacts, and all 1,321 unique blobs reachable from local Git refs before this cleanup. Pattern checks looked for GitHub and Slack tokens, OpenAI-style provider keys, AWS access-key IDs, Google API keys, private-key headers, and suspicious literal credential assignments. No matches were found. This is a bounded pattern and content review, not a guarantee that every possible sensitive value is absent.

## Presentation changes

The README now leads with the research question, N1/N2 results, C1 limitations, a measured figure, and reproduction instructions. Operational checkpoints, implementation TODOs, submission planning, speaking notes, and private Google Docs preparation/readback artifacts were removed from the current public tree and preserved in ignored local storage. Contributor instructions and resource documentation now describe reproducible research conventions rather than personal workflow or submission arrangements.

The public report and experimental evidence remain available. The offline reproduction check no longer depends on private Google Docs preparation records; it records the local research report hash instead.

## Retained historical disclosures

Frozen research artifacts retain original local paths, process commands, timestamps, program text, source snapshots, and request identities where these contribute to integrity checks. Paths can reveal the original local account and workspace names. Third-party source and licenses remain intact. Failed attempts and experimental usage records remain part of the scientific record.

Earlier Git commits still contain removed notes, Google Doc identifiers, local paths, and the author's configured Git email address. Removing a file from the current tree does not erase prior public commits or copies. The pre-cleanup scan found Google Docs references in 36 historical blobs and local paths in 111. Document links do not grant access to their private targets.

History was preserved because frozen protocols cite commit IDs and source identities. Erasing historical disclosures would require a separately planned history rewrite and updates to provenance references; it cannot retract copies already fetched. No credential rotation was indicated by the patterns checked.

## Reproduction boundary

The historical model-call budget remains exhausted. This cleanup makes no new model or evaluator calls, changes no study outcomes, and does not imply upstream disclosure, a public issue, or a claim about ordinary ShinkaEvolve failure frequency.

## Validation of the cleanup

The current checkout passed 145 tests with three optional Docker skips. Saved-evidence verification passed for all recorded studies. Local Markdown link checks found no missing targets, the changed offline reproduction script compiled, and the deterministic publication archive contained 2,762 files with no matches for its secret patterns. A new clean-environment reproduction was not run as part of this presentation cleanup.

"""Build a self-contained replay from verified saved outcomes, with no execution."""

import argparse
import hashlib
import json
from pathlib import Path

from agentqa.evidence import verify_evidence
from agentqa.recorder import replay

HTML = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentQA · Evidence replay</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;color:#192b3d;background:#f3f6fa;line-height:1.55}*{box-sizing:border-box}body{margin:0}.wrap{max-width:1080px;margin:auto;padding:40px 24px}header{padding:24px 0}h1{font-size:clamp(30px,5vw,48px);line-height:1.15;letter-spacing:-1.6px;margin:14px 0}h2{font-size:23px;margin:0 0 14px}h3{margin:0;font-size:15px}p{max-width:850px}.muted{color:#56687c}.kicker{color:#235b98;font-size:12px;letter-spacing:1.3px;font-weight:750;text-transform:uppercase}.panel{background:white;border:1px solid #dbe3ec;border-radius:14px;padding:25px;margin:22px 0;box-shadow:0 5px 22px #17355707}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.card{background:#f6f8fb;border:1px solid #e1e7ef;border-radius:9px;padding:17px}.number{font-size:25px;font-weight:700;margin:5px 0}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0}button{cursor:pointer;background:#eef3fa;border:1px solid #ced9e8;color:#244461;border-radius:7px;padding:9px 12px;font:inherit;font-size:13px}button[aria-selected=true]{background:#235b98;color:white;border-color:#235b98}code,pre{font-family:ui-monospace,monospace;font-size:12px}code{overflow-wrap:anywhere}pre{padding:16px;overflow:auto;background:#f4f7fa;border-radius:8px;white-space:pre-wrap}.badge{display:inline-block;padding:4px 9px;border-radius:6px;font-size:12px;font-weight:700;background:#f9e4e2;color:#8b332c}.good{background:#dff1e8;color:#24654c}.timeline{list-style:none;padding:0;margin:20px 0}.timeline li{border-left:2px solid #b4c9df;margin-left:9px;padding:0 0 18px 22px;position:relative}.timeline li:before{content:'';position:absolute;left:-6px;top:5px;width:10px;height:10px;background:#235b98;border-radius:50%}.timeline li:last-child{padding-bottom:0}.notice{border-left:4px solid #b98b2c;background:#fff8e9;padding:16px 20px;border-radius:0 8px 8px 0}details{margin-top:16px}summary{cursor:pointer;color:#235b98;font-weight:600}footer{font-size:12px;color:#607084;padding:15px 0}@media(max-width:700px){.grid{grid-template-columns:1fr}.wrap{padding:22px 15px}.panel{padding:18px}h1{letter-spacing:-.8px}}
</style>
<main class="wrap">
<header><div class="kicker">AgentQA / recorded pilot evidence</div><h1>Can this result be trusted?</h1><p class="muted">A passing result belongs to a particular execution and input state. Follow the publication diagnostic, generated controller and prospectively frozen controlled transfer audit.</p><span class="badge good">Replay only · no model calls or task execution</span></header>
<section class="panel"><h2>1. A changed request, an old success</h2><p class="muted">Actual local jobs through an unchanged pinned ShinkaEvolve scheduler. The process scenarios were authored; no model made these mistakes.</p><div class="tabs" id="cases" role="tablist" aria-label="Recorded source scenarios"></div><div class="grid"><div class="card"><h3>New process exit</h3><div class="number" id="exit"></div><span class="muted">from the saved process record</span></div><div class="card"><h3>Returned score</h3><div class="number" id="score"></div><span class="muted" id="flag"></span></div><div class="card"><h3>Attribution contract</h3><div style="margin-top:12px" id="attribution"></div></div></div><ol class="timeline" id="source-timeline"></ol><details><summary>Inspect recorded identities</summary><pre id="identities"></pre></details></section>
<section class="panel"><h2>2. Bind publication to its request</h2><p class="muted">A separate local adapter uses a fresh attempt directory and a host-owned receipt. Failed or incomplete publication is invalid evidence. A complete negative evaluation can still be valid.</p><div class="grid"><div class="card"><h3>Broader publication checks</h3><div class="number" id="qualification"></div><span class="muted">fixed authored cases</span></div><div class="card"><h3>Renaming pairs</h3><div class="number" id="pairs"></div><span class="muted">same verdict across both layouts</span></div><div class="card"><h3>Valid negative results</h3><div class="number">2 / 2</div><span class="muted">correctness false; evidence valid</span></div></div><details><summary>Inspect the four original adapter checks</summary><pre id="adapter"></pre></details></section>
<section class="panel"><h2>3. A generated controller handles a handoff</h2><p class="muted">In the saved coding workflow, a GPT-6.1 Sol generated program edits the implementation, verifies it, then encounters a configuration change and memory reset. These are its actual recorded actions. The model generated the controller once, rather than reasoning afresh at every step.</p><ol class="timeline" id="workflow"></ol><span class="badge good">Final outcome: functional and freshly verified</span></section>
<section class="panel"><h2>4. Do the repairs transfer?</h2><p class="muted">The two cached generated policies were frozen unchanged. All three matched selectors had already selected repair 00. Commit 7ae8dd0 was pushed before 36 trials on nine new controlled cases. The same implementer authored both splits; there is one source pool.</p><div class="grid"><div class="card"><h3>Each generated repair</h3><div class="number" id="audit-repair"></div><span class="muted">verified completion per policy</span></div><div class="card"><h3>Authored parent</h3><div class="number" id="audit-parent"></div><span class="muted">six stale-evidence completions</span></div><div class="card"><h3>Selector advantage</h3><div class="number" id="audit-difference"></div><span class="muted">same selected ID; no interval</span></div></div><p id="audit-selectors"></p><div class="tabs" id="audit-cases" role="tablist" aria-label="Recorded controlled audit cases"></div><div class="grid"><div class="card"><h3>Parent actions</h3><pre id="audit-parent-actions"></pre><span class="badge" id="audit-parent-result"></span></div><div class="card"><h3>Generated repair actions</h3><pre id="audit-repair-actions"></pre><span class="badge good" id="audit-repair-result"></span></div><div class="card"><h3>What changed?</h3><p class="muted" id="audit-explanation"></p></div></div><details><summary>Inspect frozen audit identity and case</summary><pre id="audit-identities"></pre></details></section>
<aside class="notice"><h3>What this evidence does not establish</h3><p style="margin-bottom:0">The main repair-selection hypothesis remains inconclusive. Both generated repairs passed all nine controlled cases, so the pool did not distinguish selectors. Controlled task implementations are authored; the cached policies choose verification/completion actions. This is narrow template transfer, not a natural model-failure rate, independent human blinding or full native Sakana evolution.</p></aside>
<footer><p id="verification"></p><p>Reproduce verification from the checkout: <code>agentqa verify-evidence --root .</code>. All values shown here come from saved artifacts; this page has no external dependencies or network requests.</p></footer>
</main><script type="application/json" id="data">DATA_PLACEHOLDER</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent);
const names={'nonzero-reused':'Exit 7, old files','zero-no-publication':'Exit 0, old files','partial-publication':'Partial publication','normal-publication':'Complete publication'};
function text(id,value){document.getElementById(id).textContent=String(value)}
function item(parent,title,description){const li=document.createElement('li'),h=document.createElement('strong'),p=document.createElement('div');h.textContent=title;p.textContent=description;p.className='muted';li.append(h,p);parent.append(li)}
function show(index){const row=data.source[index];document.querySelectorAll('#cases button').forEach((b,n)=>b.setAttribute('aria-selected',n===index?'true':'false'));text('exit',row.returncode);text('score',row.score);text('flag','Returned correctness: '+row.correct);const badge=document.createElement('span');badge.className='badge'+(row.expected_accept?' good':'');badge.textContent=row.expected_accept?'New bundle accepted':'Stale or mixed bundle attributed';document.getElementById('attribution').replaceChildren(badge);const list=document.getElementById('source-timeline');list.replaceChildren();item(list,'Earlier request completed','Published score 1 and correctness true.');item(list,'The request changed',row.mode==='fail'?'The new process exited 7 before publishing.':row.mode==='no_publish'?'The new process exited 0 without publishing.':row.mode==='partial'?'The new process published metrics but no correctness result.':'The new process published both result components.');item(list,'The scheduler loaded result files','Returned score '+row.score+' with correctness '+row.correct+'.');text('identities',JSON.stringify(row,null,2))}
data.source.forEach((row,index)=>{const button=document.createElement('button');button.textContent=names[row.case];button.setAttribute('role','tab');button.addEventListener('click',()=>show(index));document.getElementById('cases').append(button)});
text('qualification',data.verified.broader_qualification.contract_matches+' / '+data.verified.broader_qualification.cases);text('pairs',data.verified.broader_qualification.renaming_pairs_invariant+' / '+data.verified.broader_qualification.renaming_pairs);text('adapter',JSON.stringify(data.adapter,null,2));data.workflow.forEach(row=>item(document.getElementById('workflow'),row.label,row.detail));text('verification',data.verified.coding_traces+' coding traces and '+data.verified.publication_bundles+' publication receipts rechecked before this page was built.');show(0);
text('audit-repair',data.audit.counts['repair-00'].verified+' / 9');text('audit-parent',data.audit.counts.parent.verified+' / 9');text('audit-difference',data.audit.difference+' pp');text('audit-selectors','Source-only, generic and failure-family: repair-00, 9 / 9 each. Authored rerun reference: '+data.audit.counts['authored-rerun'].verified+' / 9; not selectable.');
function showAudit(index){const row=data.audit.cases[index];document.querySelectorAll('#audit-cases button').forEach((b,n)=>b.setAttribute('aria-selected',n===index?'true':'false'));text('audit-parent-actions',row.parent.actions.join(' → '));text('audit-repair-actions',row.repair.actions.join(' → '));text('audit-parent-result',row.parent.reason);text('audit-repair-result',row.repair.reason);document.getElementById('audit-parent-result').className='badge'+(row.parent.verified?' good':'');text('audit-explanation',row.explanation);text('audit-identities',JSON.stringify({plan_hash:data.audit.plan_hash,case:row},null,2))}
data.audit.cases.forEach((row,index)=>{const button=document.createElement('button');button.textContent=row.label;button.setAttribute('role','tab');button.addEventListener('click',()=>showAudit(index));document.getElementById('audit-cases').append(button)});showAudit(0);
</script></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    verified = verify_evidence(root)
    inputs = [root / "evidence/upstream-source-006/summary.json", root / "evidence/bound-shinka-008/summary.json",
              root / "evidence/stateful-controller-005/summary.json", root / "evidence/publication-qualification-011/summary.json"]
    source = json.loads(inputs[0].read_text())
    rows = []
    for row in source["results"]:
        if row["case"] in {"nonzero-reused", "zero-no-publication", "partial-publication", "normal-publication"}:
            rows.append({key: row[key] for key in ("case", "mode", "returncode", "expected_accept", "prior_program_sha256", "current_program_sha256", "prior_artifacts", "current_artifacts")}
                        | {"score": row["observed_result"]["metrics"]["combined_score"],
                           "correct": row["observed_result"]["correct"]["correct"]})
    adapter = [{"case": row["case"], **row["verdict"]} for row in json.loads(inputs[1].read_text())["results"]]
    generated = json.loads(inputs[2].read_text())
    trial = next(row for row in generated["results"] if row["case"]["name"] == "config")
    trace = inputs[2].parent / trial["trace"]
    assert replay(trace, trial["tip"]).verified
    inputs.append(trace)
    events = [json.loads(line) for line in trace.read_text().splitlines()]
    workflow = []
    for event in events:
        payload = event["payload"]
        if event["kind"] == "observation" and payload.get("event") == "action":
            action = payload["value"]["action"]
            workflow.append({"label": action.capitalize(), "detail": "Recorded controller action · event " + str(event["seq"])})
        elif event["kind"] == "observation" and payload.get("event") == "handoff":
            workflow.append({"label": "Configuration changed; memory reset", "detail": "Environment handoff · event " + str(event["seq"])})
    audit_folder = root / "evidence/controlled-transfer-012"
    inputs += [audit_folder / name for name in ("plan.json", "summary.json", "analysis.json")]
    audit_summary = json.loads((audit_folder / "summary.json").read_text())
    audit_analysis = json.loads((audit_folder / "analysis.json").read_text())
    audit_pool = next(iter(audit_analysis["by_pool"].values()))
    cases = []
    for case_id, label, explanation in (
        ("slug-normalization-v1:source-repair", "Source repair", "The authored implementation changed after a weak test passed. The parent reused old evidence; repair 00 requested fresh verification."),
        ("blocked-reachability-v1:config-change", "Configuration change", "The blocked-node configuration changed after verification. The implementation remained functionally correct, but the old receipt described another footprint."),
        ("discounted-ledger-v1:unrelated-docs", "Unchanged control", "Documentation changed outside the footprint. Both policies can reuse the still-current receipt. Refusal or unconditional rejection would not count as completion.")):
        pair = {}
        for candidate, key in (("parent", "parent"), ("repair-00", "repair")):
            row = next(r for r in audit_summary["results"] if r["candidate"] == candidate and r["slot_id"] == case_id)
            inputs.append(audit_folder / row["trace"])
            pair[key] = {k: row[k] for k in ("actions", "functional", "fresh", "verified", "reason", "trace_tip", "trace")}
        cases.append({"case_id": case_id, "label": label, "explanation": explanation, **pair})
    audit = {"plan_hash": audit_summary["plan_hash"], "cases": cases,
             "counts": {candidate: score["raw_counts"] for candidate, score in audit_pool["candidates"].items()},
             "decisions": audit_pool["decisions"],
             "difference": 100 * audit_analysis["family_minus_baseline"]["source-only"]["difference"]}
    data = {"source": rows, "adapter": adapter, "workflow": workflow, "audit": audit, "verified": verified}
    encoded = json.dumps(data).replace("<", "\\u003c").replace("&", "\\u0026")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(HTML.replace("DATA_PLACEHOLDER", encoded))
    manifest = {"schema": "agentqa.replay-page.v1", "model_calls": 0, "executes_candidates": False,
                "inputs": {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs},
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "html_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(), "scope": "Recorded diagnostic/development evidence and the separately frozen C1 controlled transfer pilot; native-agent main study unperformed"}
    with (args.output.parent / "manifest.json").open("x") as stream:
        json.dump(manifest, stream, indent=2)
    print(json.dumps({"output": str(args.output), "verified": verified}))


if __name__ == "__main__":
    main()

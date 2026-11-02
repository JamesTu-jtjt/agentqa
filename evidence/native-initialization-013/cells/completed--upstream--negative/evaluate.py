import argparse, json, pathlib, runpy, sys, time
p = argparse.ArgumentParser()
p.add_argument('--program_path', required=True)
p.add_argument('--results_dir', required=True)
a = p.parse_args()
s = runpy.run_path(a.program_path)['evaluate']()
r = pathlib.Path(a.results_dir)
r.mkdir(parents=True, exist_ok=True)
mode = s['mode']
print(json.dumps(s), flush=True)
if mode == 'nonzero_empty':
    sys.exit(7)
if mode == 'zero_empty':
    sys.exit(0)
if mode != 'correct_only':
    (r / 'metrics.json').write_text(json.dumps({'combined_score': s['score']}))
if mode != 'metrics_only':
    (r / 'correct.json').write_text(json.dumps({'correct': s['correct'], 'error': None}))
if mode == 'full_then_nonzero':
    sys.exit(7)
if mode == 'block_after_publication':
    (r / 'published.marker').write_text('complete output published; evaluator deliberately blocked')
    while True:
        time.sleep(.05)

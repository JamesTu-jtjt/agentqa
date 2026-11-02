import argparse, json, pathlib, sys
p = argparse.ArgumentParser()
p.add_argument('--program_path', required=True)
p.add_argument('--results_dir', required=True)
a = p.parse_args()
state = json.loads(pathlib.Path(a.program_path).read_text())
root = pathlib.Path(a.results_dir)
root.mkdir(parents=True, exist_ok=True)
if state['mode'] == 'fail':
    print('Authored evaluation failure before publication', file=sys.stderr)
    sys.exit(7)
if state['mode'] == 'no_publish':
    print('Authored zero-exit evaluation without result publication')
    sys.exit(0)
(root / 'metrics.json').write_text(json.dumps({'combined_score': state['score']}))
if state['mode'] != 'partial':
    (root / 'correct.json').write_text(json.dumps({'correct': True, 'error': None}))

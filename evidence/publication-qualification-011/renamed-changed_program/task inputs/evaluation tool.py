import argparse, json, pathlib, sys
parser = argparse.ArgumentParser()
parser.add_argument('--program_path', required=True)
parser.add_argument('--results_dir', required=True)
args = parser.parse_args()
program = pathlib.Path(args.program_path)
state = json.loads(program.read_text())
mode = state['mode']
root = pathlib.Path(args.results_dir)
root.mkdir(parents=True, exist_ok=True)
if mode == 'no_publication':
    sys.exit(0)
if mode == 'changed_program':
    program.write_text(json.dumps({**state, 'touched_during_run': True}))
if mode == 'changed_config':
    config = pathlib.Path(state['config'])
    config.write_text(json.dumps({'limit': 11}))
if mode != 'correct_only':
    metrics = {'combined_score': -.5 if mode == 'negative' else 2.5}
    if mode == 'boolean_score':
        metrics['combined_score'] = True
    text = json.dumps(metrics)
    if mode == 'duplicate_key':
        text = '{"combined_score": 2.5, "combined_score": 99}'
    (root / 'metrics.json').write_text(text)
if mode != 'metrics_only':
    (root / 'correct.json').write_text(json.dumps({'correct': mode != 'negative', 'error': None}))
if mode == 'exit_after_publication':
    sys.exit(7)

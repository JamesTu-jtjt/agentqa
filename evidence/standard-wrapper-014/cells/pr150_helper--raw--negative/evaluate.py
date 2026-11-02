import argparse, importlib.util, json, pathlib, runpy, sys
p=argparse.ArgumentParser()
p.add_argument('--program_path',required=True)
p.add_argument('--results_dir',required=True)
p.add_argument('--helper',required=True)
a=p.parse_args()
s=runpy.run_path(a.program_path)['STATE']
if s['mode'].startswith('before_'):
    sys.exit(7 if s['mode']=='before_nonzero' else 0)
spec=importlib.util.spec_from_file_location('n2_exact_upstream_helper',a.helper)
helper=importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
helper.run_shinka_eval(program_path=a.program_path,results_dir=a.results_dir,
    experiment_fn_name='run_trial',num_runs=1,get_experiment_kwargs=lambda _: {},
    aggregate_metrics_fn=lambda outputs: {'combined_score':outputs[0]['score']},
    validate_fn=lambda out: (out['correct'],None if out['correct'] else 'authored negative'),
    run_workers=1,verbose=False)

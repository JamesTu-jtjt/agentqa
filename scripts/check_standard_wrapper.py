"""Fixed no-inference test of actual upstream evaluation helpers."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from agentqa.bundles import parse_result
from agentqa.contracts import digest
from agentqa.shinka_bridge import UPSTREAM_REVISION

ROOT = Path(__file__).resolve().parents[1]
MODES = ("inside_nonzero", "inside_zero", "before_nonzero", "before_zero", "positive", "negative")
HELPERS = ("pinned", "pr150_helper")
POLICIES = ("raw", "fresh_exit_schema")
EVALUATOR = '''import argparse, importlib.util, json, pathlib, runpy, sys
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
'''


def authored_program(mode, *, primer=False):
    if mode not in MODES:
        raise ValueError("Unknown fixed mode")
    state = {"mode": mode, "score": .1 if primer else .9, "correct": mode != "negative"}
    return ("import os\nSTATE=" + repr(state) + "\ndef run_trial():\n"
            "    if STATE['mode'].startswith('inside_'):\n"
            "        os._exit(7 if STATE['mode']=='inside_nonzero' else 0)\n"
            "    return STATE\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions():
    return [{"helper": helper, "policy": policy, "mode": mode}
            for helper in HELPERS for policy in POLICIES for mode in MODES]


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--freeze',action='store_true')
    args=parser.parse_args()
    output=args.output.resolve()
    if args.freeze:
        output.mkdir(parents=True,exist_ok=False)
        for name, source in (("pinned",ROOT/'vendor/ShinkaEvolve/shinka/core/wrap_eval.py'),
                             ("pr150_helper",ROOT/'scratch/pr150-wrap_eval.py')):
            shutil.copyfile(source,output/f'{name}.py')
        shutil.copyfile(ROOT/'vendor/ShinkaEvolve/LICENSE',output/'LICENSE')
        shutil.copyfile(Path(__file__),output/'frozen-script.py')
        shutil.copyfile(ROOT/'docs/standard-wrapper-protocol.md',output/'protocol.md')
        plan={'schema':'agentqa.standard-wrapper.v1','upstream_revision':UPSTREAM_REVISION,
              'pr150_head':'7f6b67e20cd44821dd9d7df0d15d5905cefe43d8',
              'helpers':{name:sha(output/f'{name}.py') for name in HELPERS},
              'script_sha256':sha(Path(__file__)),'protocol_sha256':sha(output/'protocol.md'),
              'evaluator':EVALUATOR,'cells':definitions(),'max_evaluator_processes':48,'model_calls':0,
              'retry_policy':'none','scope':'Isolated helper modules, not the complete PR or native runner'}
        write(output/'plan.json',{**plan,'plan_hash':digest(plan)})
        return
    envelope=json.loads((output/'plan.json').read_text())
    plan={k:v for k,v in envelope.items() if k!='plan_hash'}
    if digest(plan)!=envelope['plan_hash'] or plan['script_sha256']!=sha(Path(__file__)):
        raise ValueError('N2 frozen source changed')
    if any((output/'cells').glob('*')):
        raise ValueError('Refuse repeat or overwrite of N2 cells')
    import shinka.launch.scheduler as scheduler_module
    from shinka.launch import JobScheduler,LocalJobConfig
    if not Path(scheduler_module.__file__).resolve().is_relative_to(ROOT/'vendor/ShinkaEvolve'):
        raise ValueError('Wrong native scheduler')
    rows=[]
    for cell in plan['cells']:
        name='--'.join(cell[k] for k in ('helper','policy','mode'))
        folder=output/'cells'/name
        folder.mkdir(parents=True,exist_ok=False)
        write(folder/'reservation.json',{'cell':cell,'plan_hash':envelope['plan_hash']})
        evaluator=folder/'evaluate.py';evaluator.write_text(EVALUATOR)
        source=folder/'program.py'
        helper=output/f"{cell['helper']}.py"
        if sha(helper)!=plan['helpers'][cell['helper']]:
            raise ValueError('N2 helper source changed')
        scheduler=JobScheduler('local',LocalJobConfig(eval_program_path=str(evaluator),
            python_executable=sys.executable,eval_verbose=False,numeric_threads_per_job=1,
            extra_cmd_args={'helper':str(helper)}),max_workers=1)
        def execute(results):
            started=time.monotonic()
            proc=scheduler.submit_async(str(source),str(results))
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait(timeout=5)
                raise RuntimeError('N2 evaluator timed out; preserve incomplete cell')
            raw=scheduler.get_job_results(proc,str(results))
            return {'returncode':proc.returncode,'raw':raw,'duration_seconds':time.monotonic()-started}
        try:
            source.write_text(authored_program('positive',primer=True))
            original=folder/'results'
            primer=execute(original)
            if primer['returncode']!=0 or primer['raw'].get('correct',{}).get('correct') is not True:
                write(folder/'primer-failure.json',primer)
                raise RuntimeError('N2 standard-helper primer failed')
            shutil.copytree(original,folder/'prior-results')
            source.write_text(authored_program(cell['mode']))
            target_results=original if cell['policy']=='raw' else folder/'fresh-results'
            target=execute(target_results)
            returned=target['raw']
            if cell['policy']=='fresh_exit_schema':
                try:
                    if target['returncode']!=0:
                        raise ValueError('Nonzero attempt')
                    returned={**returned,**parse_result(target_results)}
                except (OSError,ValueError,TypeError,KeyError):
                    returned={'correct':{'correct':False},'metrics':{'combined_score':0}}
            valid=cell['mode'] in {'positive','negative'}
            correct=returned.get('correct',{}).get('correct') is True
            score=returned.get('metrics',{}).get('combined_score')
            row={'cell':cell,'plan_hash':envelope['plan_hash'],'primer':primer,'target':target,'returned':returned,
                 'target_results':str(target_results.relative_to(output)),
                 'incorrect_acceptance':not valid and correct,
                 'positive_preserved':cell['mode']=='positive' and correct and score==.9,
                 'negative_preserved':cell['mode']=='negative' and not correct and score==.9}
            write(folder/'result.json',row);rows.append(row)
            print(json.dumps({'cell':name,'returncode':target['returncode'],'correct':correct,'score':score}),flush=True)
        finally:
            scheduler.shutdown()
    write(output/'outcomes.json',rows)
    hashes={str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()}
    write(output/'file-manifest.json',{'files':hashes,'files_hash':digest(hashes),'plan_hash':envelope['plan_hash']})


if __name__=='__main__':
    main()

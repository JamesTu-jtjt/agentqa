import os
STATE={'mode': 'before_nonzero', 'score': 0.9, 'correct': True}
def run_trial():
    if STATE['mode'].startswith('inside_'):
        os._exit(7 if STATE['mode']=='inside_nonzero' else 0)
    return STATE

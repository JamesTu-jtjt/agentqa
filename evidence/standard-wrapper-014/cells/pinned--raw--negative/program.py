import os
STATE={'mode': 'negative', 'score': 0.9, 'correct': False}
def run_trial():
    if STATE['mode'].startswith('inside_'):
        os._exit(7 if STATE['mode']=='inside_nonzero' else 0)
    return STATE

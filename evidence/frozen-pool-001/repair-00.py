def choose_action(observation):
    evidence = observation.get('evidence') or {}
    current = observation.get('current_fingerprint')
    if (current and evidence.get('fingerprint') == current
            and evidence.get('status') == 'passed'):
        return 'complete'
    return 'verify'

def choose_action(observation):
    evidence = observation.get('evidence') or {}
    current = observation.get('current_fingerprint')
    if (current is not None
            and evidence.get('record_id')
            and evidence.get('status') == 'passed'
            and evidence.get('fingerprint') == current):
        return 'complete'
    return 'verify'

def choose_action(observation):
    evidence = observation.get('evidence') or {}
    current = observation.get('current_fingerprint')
    valid = (
        bool(evidence.get('record_id'))
        and bool(current)
        and evidence.get('fingerprint') == current
        and evidence.get('status') == 'passed'
    )
    return 'complete' if valid else 'verify'

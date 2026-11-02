import keyword


def choose_action(observation, memory):
    memory = memory if isinstance(memory, dict) else {}
    last = observation.get('last_tool') or {}

    def emit(action, phase=None, **arguments):
        state = {} if phase is None else {'phase': phase}
        return {'action': action, 'memory': state, **arguments}

    # Never retry a reported verification failure.
    if last.get('tool') == 'verify':
        if (last.get('status') != 'passed'
                or last.get('returncode') != 0
                or last.get('before') is None
                or last.get('before') != last.get('after')):
            return emit('refuse')
        return emit('status', 'after_verify')

    name = observation.get('function')
    path = observation.get('module')
    if (not isinstance(name, str) or not name.isidentifier()
            or keyword.iskeyword(name)
            or path not in observation.get('files', [])):
        return emit('refuse')

    source = (
        'def ' + name + '(value, limit):\n'
        '    """Clip an integer to the inclusive interval [0, limit]."""\n'
        '    return min(max(value, 0), limit)\n'
    )
    phase = memory.get('phase')

    # Handoffs discard assumptions about both source and evidence freshness.
    if last.get('tool') == 'handoff' or phase is None:
        return emit('read', 'reading', path=path)

    if phase == 'reading':
        if last.get('tool') != 'read' or last.get('path') != path:
            return emit('refuse')
        if last.get('content') != source:
            return emit('write', 'writing', path=path, content=source)
        return emit('status', 'before_verify')

    if phase == 'writing':
        if (last.get('tool') != 'write' or last.get('path') != path
                or last.get('status') != 'written'):
            return emit('refuse')
        return emit('status', 'before_verify')

    if phase in ('before_verify', 'after_verify'):
        if last.get('tool') != 'status':
            return emit('refuse')
        fingerprint = last.get('current_fingerprint')
        if fingerprint is None:
            return emit('refuse')
        receipt = last.get('evidence')
        fresh = (
            isinstance(receipt, dict)
            and receipt.get('status') == 'passed'
            and receipt.get('returncode') == 0
            and receipt.get('record_id') is not None
            and receipt.get('before') == fingerprint
            and receipt.get('after') == fingerprint
        )
        if fresh:
            return emit('complete')
        if phase == 'after_verify':
            # Relevant inputs changed: inspect the module again before checking.
            return emit('read', 'reading', path=path)
        return emit('verify', 'verifying')

    return emit('refuse')

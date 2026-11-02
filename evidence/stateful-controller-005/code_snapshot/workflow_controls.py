"""Labeled authored measurement controls; never model-discovered repairs."""

REFERENCE = '''def choose_action(observation, memory):
    tool = observation.get("last_tool") or {}
    kind = tool.get("tool")
    if kind == "read":
        if "raise NotImplementedError" in tool["content"]:
            source = "def " + observation["function"] + "(value, limit):\\n    return max(0, min(value, limit))\\n"
            return {"action": "write", "path": observation["module"], "content": source, "memory": {}}
        return {"action": "status", "memory": {}}
    if kind == "status":
        evidence = tool.get("evidence") or {}
        fresh = (evidence.get("status") == "passed" and evidence.get("before") == tool["current_fingerprint"]
                 and evidence.get("after") == tool["current_fingerprint"])
        return {"action": "complete" if fresh else "verify", "memory": {}}
    if kind in ("write", "verify"):
        return {"action": "status", "memory": {}}
    return {"action": "read", "path": observation["module"], "memory": {}}
'''

STALE_CONTROL = '''def choose_action(observation, memory):
    tool = observation.get("last_tool") or {}
    kind = tool.get("tool")
    if kind == "handoff" and observation.get("evidence"):
        return {"action": "complete", "memory": {}}
    if kind == "read":
        source = "def " + observation["function"] + "(value, limit):\\n    return max(0, min(value, limit))\\n"
        return {"action": "write", "path": observation["module"], "content": source, "memory": {}}
    if kind in ("write", "handoff"):
        return {"action": "verify", "memory": {}}
    if kind == "verify":
        return {"action": "complete", "memory": {}}
    return {"action": "read", "path": observation["module"], "memory": {}}
'''

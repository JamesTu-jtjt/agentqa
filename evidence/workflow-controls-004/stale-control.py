def choose_action(observation, memory):
    tool = observation.get("last_tool") or {}
    kind = tool.get("tool")
    if kind == "handoff" and observation.get("evidence"):
        return {"action": "complete", "memory": {}}
    if kind == "read":
        source = "def " + observation["function"] + "(value, limit):\n    return max(0, min(value, limit))\n"
        return {"action": "write", "path": observation["module"], "content": source, "memory": {}}
    if kind in ("write", "handoff"):
        return {"action": "verify", "memory": {}}
    if kind == "verify":
        return {"action": "complete", "memory": {}}
    return {"action": "read", "path": observation["module"], "memory": {}}

"""Execute a generated pure decision function only inside the Docker worker."""

import json

from .sandbox import DockerWorker


class GeneratedPolicy:
    def __init__(self, program: str, worker: DockerWorker | None = None):
        self.program = program
        self.worker = worker or DockerWorker()
        self.results = []

    def next_action(self, observation: dict) -> str:
        script = ("import json\n"
                  f"namespace = {{}}\nexec({self.program!r}, namespace)\n"
                  f"observation = json.loads({json.dumps(observation)!r})\n"
                  "action = namespace['choose_action'](observation)\n"
                  "print(json.dumps({'action': action}))\n")
        result = self.worker.run(script)
        self.results.append(result.to_dict())
        if result.status != "completed" or not result.cleanup_confirmed:
            raise RuntimeError(f"Candidate execution failed: {result.status}")
        try:
            value = json.loads(result.output)
            action = value["action"]
        except (ValueError, KeyError, TypeError) as exc:
            raise RuntimeError("Candidate did not return a single action JSON object") from exc
        if action not in ("verify", "complete", "refuse"):
            raise RuntimeError("Candidate returned an unsupported action")
        return action

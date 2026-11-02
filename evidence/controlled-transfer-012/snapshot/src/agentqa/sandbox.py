"""Resource-bounded Docker worker with no host mounts or provider credentials.

This is an execution primitive, not the completed candidate/evaluator bridge.
"""

from dataclasses import asdict, dataclass
import os
import re
import selectors
import subprocess
import time
import uuid

PYTHON_IMAGE = "python@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419"


@dataclass(frozen=True)
class SandboxResult:
    status: str
    returncode: int | None
    output: str
    duration_seconds: float
    container_name: str
    cleanup_confirmed: bool
    failure_phase: str | None = None
    startup_seconds: float | None = None

    def to_dict(self):
        return asdict(self)


class DockerWorker:
    def __init__(self, image: str = PYTHON_IMAGE):
        if not re.fullmatch(r"[a-zA-Z0-9./_-]+@sha256:[a-f0-9]{64}", image):
            raise ValueError("Docker image must be pinned by digest")
        self.image = image

    def run(self, program: str, *, timeout: float = 10, output_limit: int = 16384,
            startup_timeout: float = 30) -> SandboxResult:
        source = program.encode()
        if (len(source) > 65536 or not 0 < timeout <= 60 or not 0 < output_limit <= 1048576
                or not 0 < startup_timeout <= 60):
            raise ValueError("Program or execution limits exceed the worker bounds")
        name = "agentqa-" + uuid.uuid4().hex
        command = ["docker", "run", "--rm", "--pull=never", "--name", name,
                   "--network=none", "--read-only", "--cap-drop=ALL",
                   "--security-opt=no-new-privileges", "--pids-limit=32",
                   "--memory=128m", "--memory-swap=128m", "--cpus=0.5",
                   "--user=65534:65534", "--log-driver=none",
                   "--ulimit", "fsize=1048576:1048576",
                   "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
                   "--tmpfs", "/workspace:rw,nosuid,size=16m,uid=65534,gid=65534",
                   "--workdir=/workspace", "-i", self.image, "python", "-I", "-B", "-"]
        started = time.monotonic()
        ready_marker = f"agentqa-ready-{uuid.uuid4().hex}\n".encode()
        # The trusted wrapper signals readiness before executing any candidate code.
        source = (f"print({ready_marker.decode().strip()!r}, flush=True)\n"
                  f"exec(compile({program!r}, '<candidate>', 'exec'))\n").encode()
        ready_at = None
        prelude = bytearray()
        failure_phase = None
        captured = bytearray()
        status = "infrastructure_error"
        code = None
        process = None
        cleanup = False
        try:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            assert process.stdin and process.stdout
            with selectors.DefaultSelector() as selector:
                # Nonblocking stdin avoids hanging while Docker starts or the daemon fails.
                os.set_blocking(process.stdin.fileno(), False)
                os.set_blocking(process.stdout.fileno(), False)
                selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
                selector.register(process.stdout, selectors.EVENT_READ, "stdout")
                offset = 0
                while selector.get_map():
                    now = time.monotonic()
                    if ((ready_at is None and now - started >= startup_timeout)
                            or (ready_at is not None and now - ready_at >= timeout)):
                        status = "timeout"
                        failure_phase = "startup" if ready_at is None else "execution"
                        break
                    limited = False
                    for key, _ in selector.select(timeout=0.05):
                        if key.data == "stdin":
                            try:
                                offset += os.write(key.fd, source[offset:offset + 4096])
                            except BrokenPipeError:
                                offset = len(source)
                            if offset >= len(source):
                                selector.unregister(key.fileobj)
                                process.stdin.close()
                        else:
                            chunk = os.read(key.fd, 65536)
                            if not chunk:
                                selector.unregister(key.fileobj)
                            else:
                                if ready_at is None:
                                    prelude.extend(chunk)
                                    if b"\n" not in prelude:
                                        if len(prelude) > output_limit:
                                            status, failure_phase, limited = "output_limit", "startup", True
                                            break
                                        continue
                                    if not prelude.startswith(ready_marker):
                                        captured.extend(prelude[:output_limit])
                                        status, failure_phase, limited = "infrastructure_error", "startup", True
                                        break
                                    ready_at = time.monotonic()
                                    chunk = bytes(prelude[len(ready_marker):])
                                    prelude.clear()
                                remaining = output_limit - len(captured)
                                captured.extend(chunk[:remaining])
                                if len(chunk) > remaining:
                                    status = "output_limit"
                                    failure_phase = "execution"
                                    limited = True
                                    break
                    if limited:
                        break
                else:
                    code = process.wait(timeout=2)
                    status = "completed" if code == 0 and ready_at is not None else (
                        "infrastructure_error" if ready_at is None or code == 125 else "failed")
                    if ready_at is None:
                        captured.extend(prelude[:output_limit])
                        failure_phase = "startup"
        except subprocess.TimeoutExpired:
            status = "timeout"
            failure_phase = "startup" if ready_at is None else "execution"
        except OSError as exc:
            captured.extend(str(exc).encode()[:max(0, output_limit - len(captured))])
            status = "infrastructure_error"
        finally:
            # Cleanup refers exclusively to this call's random container name.
            try:
                removed = subprocess.run(["docker", "rm", "-f", name], capture_output=True, timeout=10)
                cleanup = removed.returncode == 0 or b"No such container" in removed.stderr
                # --rm may already be removing an exited container when rm -f races it.
                # Confirm absence rather than interpreting that race as a leaked worker.
                for _ in range(3):
                    check = subprocess.run(["docker", "ps", "-aq", "--filter", f"name=^/{name}$"],
                                           capture_output=True, timeout=3)
                    if check.returncode == 0 and not check.stdout.strip():
                        cleanup = True
                        break
                    time.sleep(0.05)
            except (OSError, subprocess.TimeoutExpired):
                cleanup = False
            if process is not None:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                if process.stdin and not process.stdin.closed:
                    process.stdin.close()
                if process.stdout:
                    process.stdout.close()
        return SandboxResult(status, code, captured.decode(errors="replace"),
                             time.monotonic() - started, name, cleanup, failure_phase,
                             ready_at - started if ready_at is not None else None)

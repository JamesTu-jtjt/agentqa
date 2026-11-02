"""Versioned contract and content identity for bounded deterministic fixtures."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path, PurePosixPath
import platform

SCHEMA = "agentqa.trace.v1"
CONTRACT = "fresh-content.v1"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def safe_path(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if (not name or relative.is_absolute() or "\\" in name
            or any(part in ("", ".", "..") for part in name.split("/"))):
        raise ValueError(f"Unsafe relative path: {name!r}")
    current = root
    if root.is_symlink():
        raise ValueError("Workspace must not be a symlink")
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink not allowed: {name}")
    if current.exists() and (not current.is_file() or current.stat().st_nlink != 1):
        raise ValueError(f"Expected a regular unlinked file: {name}")
    return current


@dataclass(frozen=True)
class Scenario:
    scenario_id: str = "clamp-source"
    template_id: str = "clamp-development-v1"
    module: str = "clamp.py"
    visible_test: str = "test_visible.py"
    config: str = "config.json"
    function: str = "clamp"
    invalidate: bool = True
    noise: int = 0
    carrier: str = "transcript"
    compact: bool = False

    def __post_init__(self):
        if not self.function.isidentifier() or self.function.startswith("__"):
            raise ValueError("Invalid function name")
        if len(set(self.footprint)) != 3:
            raise ValueError("Footprint paths must be distinct")
        for path in self.footprint:
            safe_path(Path("/nonexistent-agentqa-schema"), path)
        if self.carrier not in ("transcript", "cache", "handoff"):
            raise ValueError("Unsupported evidence carrier")
        if not 0 <= self.noise <= 100:
            raise ValueError("Noise exceeds supported context bound")

    @property
    def footprint(self) -> tuple[str, ...]:
        return (self.module, self.visible_test, self.config)

    @property
    def identity(self) -> str:
        return digest(asdict(self))


def fingerprint(root: Path, scenario: Scenario) -> str:
    files = {}
    for name in sorted(scenario.footprint):
        path = safe_path(root, name)
        files[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    return digest({"contract": CONTRACT, "files": files,
                   "runtime": {"implementation": platform.python_implementation(),
                               "python": platform.python_version()},
                   "dependencies": "stdlib-only"})


@dataclass(frozen=True)
class Verdict:
    completed: bool
    functional: bool
    fresh: bool
    verified: bool
    reason: str

    def to_dict(self) -> dict:
        return asdict(self)

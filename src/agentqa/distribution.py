"""Deterministic source/evidence bundles with explicit publication boundaries."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

FORBIDDEN_PARTS = {".git", ".venv", "vendor", "scratch", "runs", "__pycache__", ".pytest_cache"}
SECRET_PATTERNS = {
    "github_token": re.compile(rb"(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}"),
    "provider_key": re.compile(rb"sk-(?:proj-)?[A-Za-z0-9_-]{32,}"),
    "private_key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def inventory(root: Path):
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=root, capture_output=True, check=True)
    return sorted(set(name.decode() for name in result.stdout.split(b"\0") if name))


def inspect_files(root: Path, names: list[str]):
    files, findings = {}, []
    for name in names:
        relative = PurePosixPath(name)
        if (relative.is_absolute() or "\\" in name or any(part in {"", ".", ".."} for part in name.split("/"))
                or set(relative.parts) & FORBIDDEN_PARTS):
            raise ValueError(f"Forbidden publication path: {name}")
        if relative.name in {"auth.json", "credentials.json", "credentials", ".env"} or relative.name.startswith(".env."):
            raise ValueError(f"Credential/environment filename excluded: {name}")
        path = root
        for part in relative.parts:
            path /= part
            if path.is_symlink():
                raise ValueError(f"Symlink excluded from publication: {name}")
        if not path.is_file() or path.stat().st_nlink != 1:
            raise ValueError(f"Expected regular unlinked file: {name}")
        if path.stat().st_size > 20 * 1024 * 1024:
            raise ValueError(f"File exceeds the small reproduction-bundle bound: {name}")
        data = path.read_bytes()
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                findings.append({"file": name, "rule": label})
        files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return {"schema": "agentqa.publication-inventory.v1", "files": files,
            "file_count": len(files), "total_bytes": sum(row["bytes"] for row in files.values()),
            "secret_pattern_findings": findings,
            "scan_limit": "Pattern scan and explicit path boundary, not a guarantee that arbitrary secrets cannot exist"}


def create_bundle(root: Path, output: Path, names: list[str] | None = None):
    manifest = inspect_files(root, names if names is not None else inventory(root))
    if manifest["secret_pattern_findings"]:
        raise ValueError("Potential secret material found; publication refused (values are never printed)")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        payloads = {name: (root / name).read_bytes() for name in manifest["files"]}
        payloads["REPRODUCTION_MANIFEST.json"] = json.dumps(manifest, sort_keys=True, indent=2).encode()
        for name in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payloads[name])
    return manifest


def verify_archive(archive_path: Path):
    with zipfile.ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("REPRODUCTION_MANIFEST.json"))
        expected = set(manifest["files"]) | {"REPRODUCTION_MANIFEST.json"}
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != expected:
            raise ValueError("Unexpected/duplicate archive members")
        for name, row in manifest["files"].items():
            relative = PurePosixPath(name)
            if relative.is_absolute() or any(part in {"", ".", ".."} for part in name.split("/")):
                raise ValueError("Unsafe archive member")
            data = archive.read(name)
            if len(data) != row["bytes"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("Archive content differs from reproduction manifest")
    return {"file_count": manifest["file_count"], "total_bytes": manifest["total_bytes"],
            "sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest()}

import hashlib
from pathlib import Path
import zipfile

import pytest

from agentqa.distribution import create_bundle, inspect_files, verify_archive


def test_archive_is_deterministic_and_manifest_checked(tmp_path):
    (tmp_path / "source.py").write_text("print('authored example')\n")
    first, second = tmp_path / "a.zip", tmp_path / "b.zip"
    create_bundle(tmp_path, first, ["source.py"])
    create_bundle(tmp_path, second, ["source.py"])
    assert first.read_bytes() == second.read_bytes()
    assert verify_archive(first)["file_count"] == 1
    with pytest.raises(FileExistsError):
        create_bundle(tmp_path, first, ["source.py"])


@pytest.mark.parametrize("name", (".git/config", "../outside", ".env", "runs/secret.txt"))
def test_runtime_credentials_and_outside_paths_cannot_be_published(tmp_path, name):
    with pytest.raises(ValueError):
        inspect_files(tmp_path, [name])


def test_symlink_and_secret_values_block_archive_without_printing_value(tmp_path):
    (tmp_path / "target").write_text("local")
    (tmp_path / "link").symlink_to(tmp_path / "target")
    with pytest.raises(ValueError, match="Symlink"):
        inspect_files(tmp_path, ["link"])
    # Construct a synthetic test token without putting a token-shaped literal in source.
    value = "g" + "hp_" + "A" * 36
    (tmp_path / "sensitive.txt").write_text(value)
    scan = inspect_files(tmp_path, ["sensitive.txt"])
    assert scan["secret_pattern_findings"] == [{"file": "sensitive.txt", "rule": "github_token"}]
    assert value not in str(scan)
    with pytest.raises(ValueError, match="refused"):
        create_bundle(tmp_path, tmp_path / "refused.zip", ["sensitive.txt"])
    assert not (tmp_path / "refused.zip").exists()


def test_extra_archive_member_is_not_accepted(tmp_path):
    (tmp_path / "source").write_text("x")
    path = tmp_path / "bundle.zip"
    create_bundle(tmp_path, path, ["source"])
    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr("unlisted", "bad")
    with pytest.raises(ValueError, match="Unexpected"):
        verify_archive(path)

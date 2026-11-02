import hashlib
from pathlib import Path
import shutil

import pytest

from agentqa.native_replay import verify_native_study

SAVED = Path(__file__).resolve().parents[1] / "evidence/native-initialization-013"


def file_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def test_native_databases_replay_without_mutating_any_source_file():
    before = file_hashes(SAVED)
    result = verify_native_study(SAVED)
    assert result["cells"] == result["native_databases"] == 56
    assert result["evaluator_processes"] == 105
    assert result["interrupted_primers"] == result["bound_receipts"] == 7
    assert result["analysis"]["defenses"]["fresh_exit_schema"]["incorrect_acceptance"] == 0
    assert result["analysis"]["defenses"]["bound"]["incorrect_acceptance"] == 0
    assert before == file_hashes(SAVED)


@pytest.mark.parametrize("artifact", ("analysis.json", "outcomes.json",
    "cells/interrupted--upstream--nonzero_empty/native/programs.sqlite",
    "cells/interrupted--upstream--nonzero_empty/native/programs.sqlite-wal"))
def test_changed_durable_native_evidence_is_rejected(tmp_path, artifact):
    copy = tmp_path / "evidence"
    shutil.copytree(SAVED, copy)
    path = copy / artifact
    with path.open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="artifact changed"):
        verify_native_study(copy)

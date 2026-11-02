from dataclasses import asdict

import pytest

from agentqa.native_study import Cell, analyze_rows, cells, grade, program


def row(cell, *, correct=False, score=0, archive=False, best=False):
    current = {"id": "target", "code": program(cell.mode), "correct": correct, "combined_score": score}
    database = {"programs": [current], "archive": ["target"] if archive else [],
                "metadata": {"best_program_id": "target" if best else "other"}}
    return {"cell": asdict(cell), "current": current, "database": database,
            "target_report": {"total_proposals_generated": 0}, "grade": grade(cell, current, database)}


def test_invalid_acceptance_archive_and_best_are_distinct():
    cell = Cell("completed", "upstream", "metrics_only")
    observed = row(cell, correct=True, score=.9, archive=True)
    assert observed["grade"]["incorrect_acceptance"]
    assert observed["grade"]["incorrect_archive"]
    assert not observed["grade"]["incorrect_best"]
    rejected_with_old_score = row(cell, correct=False, score=.1)
    assert not rejected_with_old_score["grade"]["incorrect_acceptance"]
    assert rejected_with_old_score["grade"]["invalid_nonzero_score"]


def test_legitimate_negative_preserves_score_without_becoming_success():
    observed = row(Cell("completed", "bound", "negative"), correct=False, score=.9)
    assert observed["grade"]["negative_preserved"]
    assert not observed["grade"]["incorrect_acceptance"]
    assert not observed["grade"]["positive_preserved"]


def test_native_analysis_requires_complete_unique_grid():
    rows = [row(cell) for cell in cells()]
    assert len(rows) == len({cell.name for cell in cells()}) == 56
    result = analyze_rows(rows)
    assert result["defenses"]["bound"]["cells"] == 7
    assert result["confidence_interval"] is None
    for changed in (rows[:-1], rows + [rows[0]]):
        with pytest.raises(ValueError):
            analyze_rows(changed)


def test_analysis_rejects_forged_grade_or_model_proposal():
    rows = [row(cell) for cell in cells()]
    rows[0]["grade"]["incorrect_acceptance"] = True
    with pytest.raises(ValueError, match="grade changed"):
        analyze_rows(rows)
    rows = [row(cell) for cell in cells()]
    rows[0]["target_report"]["total_proposals_generated"] = 1
    with pytest.raises(ValueError, match="model proposal"):
        analyze_rows(rows)


def test_grade_rejects_other_source_even_if_behavior_matches():
    cell = Cell("fresh", "upstream", "positive")
    observed = row(cell, correct=True, score=.9)
    observed["current"]["code"] += "# different source\n"
    with pytest.raises(ValueError, match="frozen authored source"):
        grade(cell, observed["current"], observed["database"])

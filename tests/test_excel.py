from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from openpyxl import load_workbook

from greenshot_to_punchlist import excel


@pytest.fixture
def screenshot(tmp_path: Path) -> Path:
    p = tmp_path / "shot.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n")
    return p


def make_row(screenshot: Path, **overrides) -> excel.Row:
    defaults = dict(
        project="Project Alpha",
        discipline="ARCH",
        issue="Door clashes with column",
        priority="High",
        assigned_to="J. Smith",
        status="Open",
        screenshot_path=screenshot,
    )
    defaults.update(overrides)
    return excel.Row(**defaults)


def test_creates_workbook_with_headers_and_appends_first_row(tmp_path, screenshot):
    path = excel.workbook_path_for("Project Alpha", tmp_path)
    assert not path.exists()

    n = excel.append_row(
        path,
        make_row(screenshot),
        disciplines=["ARCH", "STRUCT"],
        priorities=["High", "Low"],
        today=date(2026, 4, 29),
    )

    assert n == 1
    assert path.exists()

    wb = load_workbook(path)
    ws = wb["Punchlist"]
    headers = [c.value for c in ws[1]]
    assert headers == excel.HEADERS

    row2 = [c.value for c in ws[2]]
    assert row2[0] == 1
    assert row2[1] == "2026-04-29"
    assert row2[2] == "Project Alpha"
    assert row2[3] == "ARCH"
    assert row2[4] == "Door clashes with column"
    assert row2[5] == "High"
    assert row2[6] == "J. Smith"
    assert row2[7] == "Open"
    assert row2[8] == "shot.png"

    link_cell = ws.cell(row=2, column=10)
    assert link_cell.value == "Open"
    assert link_cell.hyperlink is not None
    assert link_cell.hyperlink.target == str(screenshot.resolve())


def test_second_append_increments_number(tmp_path, screenshot):
    path = excel.workbook_path_for("Project Alpha", tmp_path)

    excel.append_row(path, make_row(screenshot), today=date(2026, 4, 29))
    n = excel.append_row(path, make_row(screenshot, issue="Second issue"), today=date(2026, 4, 29))

    assert n == 2

    wb = load_workbook(path)
    ws = wb["Punchlist"]
    assert ws.max_row == 3
    assert ws.cell(row=3, column=1).value == 2
    assert ws.cell(row=3, column=5).value == "Second issue"


def test_per_project_workbook_paths(tmp_path):
    p1 = excel.workbook_path_for("Project Alpha", tmp_path)
    p2 = excel.workbook_path_for("Project / Beta?", tmp_path)
    assert p1.name == "Project Alpha.xlsx"
    assert p2.name == "Project _ Beta_.xlsx"


def test_sanitize_handles_empty():
    assert excel.sanitize_project_name("") == "punchlist"
    assert excel.sanitize_project_name("///") == "punchlist"


def test_freeze_panes_and_header_style(tmp_path, screenshot):
    path = excel.workbook_path_for("Alpha", tmp_path)
    excel.append_row(path, make_row(screenshot))

    wb = load_workbook(path)
    ws = wb["Punchlist"]
    assert ws.freeze_panes == "A2"
    assert ws["A1"].font.bold is True

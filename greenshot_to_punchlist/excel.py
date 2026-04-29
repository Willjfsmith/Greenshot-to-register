"""Workbook create/append for the punchlist.

One workbook per project. Each row records a screenshot-derived issue with a
clickable hyperlink back to the original image file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


HEADERS = [
    "No.",
    "Date",
    "Project",
    "Discipline",
    "Issue",
    "Priority",
    "Assigned To",
    "Status",
    "Screenshot Filename",
    "Image Link",
]

COLUMN_WIDTHS = {
    "A": 6,
    "B": 12,
    "C": 18,
    "D": 12,
    "E": 60,
    "F": 10,
    "G": 18,
    "H": 12,
    "I": 32,
    "J": 14,
}

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_ALIGN = Alignment(vertical="center")
HYPERLINK_FONT = Font(color="0563C1", underline="single")
WRAP_ALIGN = Alignment(wrap_text=True, vertical="top")

_INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]+')


@dataclass
class Row:
    project: str
    discipline: str
    issue: str
    priority: str
    assigned_to: str
    status: str
    screenshot_path: Path


def sanitize_project_name(name: str) -> str:
    cleaned = _INVALID_FILENAME_CHARS.sub("_", name).strip().rstrip(".")
    if not cleaned or not cleaned.strip("._ "):
        return "punchlist"
    return cleaned


def workbook_path_for(project: str, workbook_dir: Path) -> Path:
    return workbook_dir / f"{sanitize_project_name(project)}.xlsx"


def _create_workbook(path: Path, disciplines: list[str], priorities: list[str]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Punchlist"
    ws.append(HEADERS)

    for col, width in COLUMN_WIDTHS.items():
        ws.column_dimensions[col].width = width

    for col_idx, _ in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN

    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"

    if disciplines:
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(disciplines)}"',
            allow_blank=True,
        )
        dv.add(f"D2:D1048576")
        ws.add_data_validation(dv)
    if priorities:
        dv = DataValidation(
            type="list",
            formula1=f'"{",".join(priorities)}"',
            allow_blank=True,
        )
        dv.add(f"F2:F1048576")
        ws.add_data_validation(dv)

    dv_status = DataValidation(
        type="list",
        formula1='"Open,In Progress,Resolved,Closed"',
        allow_blank=True,
    )
    dv_status.add("H2:H1048576")
    ws.add_data_validation(dv_status)

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def _next_number(ws) -> int:
    max_n = 0
    for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
        value = row[0]
        if isinstance(value, int) and value > max_n:
            max_n = value
        elif isinstance(value, str) and value.strip().isdigit():
            n = int(value.strip())
            if n > max_n:
                max_n = n
    return max_n + 1


def append_row(
    path: Path,
    row: Row,
    *,
    disciplines: list[str] | None = None,
    priorities: list[str] | None = None,
    today: date | None = None,
) -> int:
    """Append a row to the workbook at `path`. Creates it if missing.

    Returns the auto-assigned issue number.
    Raises PermissionError if the workbook is open in Excel.
    """
    if not path.exists():
        _create_workbook(path, disciplines or [], priorities or [])

    wb = load_workbook(path)
    ws = wb["Punchlist"] if "Punchlist" in wb.sheetnames else wb.active

    number = _next_number(ws)
    today = today or date.today()

    screenshot = row.screenshot_path
    filename = screenshot.name
    abs_path = str(screenshot.resolve())

    new_row = [
        number,
        today.isoformat(),
        row.project,
        row.discipline,
        row.issue,
        row.priority,
        row.assigned_to,
        row.status,
        filename,
        "Open",  # placeholder; replaced with hyperlink below
    ]
    ws.append(new_row)

    excel_row = ws.max_row
    link_cell = ws.cell(row=excel_row, column=len(HEADERS))
    link_cell.value = "Open"
    link_cell.hyperlink = abs_path
    link_cell.font = HYPERLINK_FONT

    issue_cell = ws.cell(row=excel_row, column=5)
    issue_cell.alignment = WRAP_ALIGN

    wb.save(path)
    return number

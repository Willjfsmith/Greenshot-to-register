"""Entrypoint: parse argv, show form, append to Excel."""

from __future__ import annotations

import sys
from pathlib import Path

from . import config as config_module
from . import excel
from . import ui


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        ui.show_error(
            "Punchlist",
            "No screenshot path was provided.\n\n"
            "This tool is intended to be launched by Greenshot's "
            "External Command plugin with the screenshot path as an argument.",
        )
        return 2

    screenshot_path = Path(argv[0]).expanduser()
    if not screenshot_path.exists():
        ui.show_error(
            "Punchlist",
            f"Screenshot file not found:\n{screenshot_path}",
        )
        return 2

    cfg = config_module.load()
    if cfg.is_default:
        ui.show_message(
            "Punchlist - first run",
            "No config.json was found. A config.example.json has been written "
            "next to the application. Rename it to config.json and edit the "
            "project list, then take a screenshot to try again.",
        )
        return 0

    form = ui.show_form(cfg, screenshot_path)
    if form is None:
        return 0

    workbook_dir = config_module.workbook_dir_for(cfg)
    workbook_dir.mkdir(parents=True, exist_ok=True)
    path = excel.workbook_path_for(form.project, workbook_dir)

    row = excel.Row(
        project=form.project,
        discipline=form.discipline,
        issue=form.issue,
        priority=form.priority,
        assigned_to=form.assigned_to,
        status=form.status,
        screenshot_path=screenshot_path,
    )

    while True:
        try:
            number = excel.append_row(
                path,
                row,
                disciplines=cfg.disciplines,
                priorities=cfg.priorities,
            )
            break
        except PermissionError:
            if not ui.ask_retry(
                "Punchlist - file in use",
                f"Could not write to:\n{path}\n\n"
                "It looks like the workbook is open in Excel. Close it and retry.",
            ):
                return 1

    ui.show_message(
        "Punchlist",
        f"Logged issue #{number} to {path.name}.",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

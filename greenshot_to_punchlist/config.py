"""Config resolution.

Looks for config.json next to the running exe (or the package, when running
from source). Falls back to built-in defaults and writes config.example.json
on first run if no config is present.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path


DEFAULTS: dict = {
    "workbook_dir": "",
    "projects": ["<edit me>"],
    "disciplines": ["ARCH", "STRUCT", "MECH", "ELEC", "CIVIL"],
    "priorities": ["High", "Medium", "Low"],
    "assignees": [],
}


@dataclass
class Config:
    workbook_dir: str = ""
    projects: list[str] = field(default_factory=list)
    disciplines: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    source_path: Path | None = None
    is_default: bool = False


def exe_dir() -> Path:
    # When frozen by PyInstaller, sys.executable is the .exe path. When running
    # from source, fall back to the package's parent directory.
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def config_path() -> Path:
    return exe_dir() / "config.json"


def example_path() -> Path:
    return exe_dir() / "config.example.json"


def load() -> Config:
    path = config_path()
    if path.exists():
        data = {**DEFAULTS, **json.loads(path.read_text(encoding="utf-8"))}
        return Config(
            workbook_dir=data["workbook_dir"],
            projects=list(data["projects"]),
            disciplines=list(data["disciplines"]),
            priorities=list(data["priorities"]),
            assignees=list(data["assignees"]),
            source_path=path,
            is_default=False,
        )

    # No config — write the example file next to the exe so the user has
    # something to edit, and return defaults.
    write_example_if_missing()
    return Config(
        workbook_dir=DEFAULTS["workbook_dir"],
        projects=list(DEFAULTS["projects"]),
        disciplines=list(DEFAULTS["disciplines"]),
        priorities=list(DEFAULTS["priorities"]),
        assignees=list(DEFAULTS["assignees"]),
        source_path=None,
        is_default=True,
    )


def write_example_if_missing() -> Path:
    path = example_path()
    if not path.exists():
        path.write_text(json.dumps(DEFAULTS, indent=2) + "\n", encoding="utf-8")
    return path


def workbook_dir_for(cfg: Config) -> Path:
    if cfg.workbook_dir.strip():
        return Path(cfg.workbook_dir).expanduser()
    return exe_dir()

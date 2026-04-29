# CLAUDE.md

Project notes for future Claude Code sessions on this repo.

## What this is

A small Windows tool that Greenshot's External Command plugin invokes after a screenshot is saved. It pops a tkinter form, captures issue metadata, and appends a row (with a clickable hyperlink to the image) to a per-project `.xlsx` punchlist.

Entry point: `python -m greenshot_to_punchlist "<screenshot_path>"`.
Packaged form: `dist/greenshot-to-punchlist.exe "<screenshot_path>"`.

## Layout

```
greenshot_to_punchlist/
  __main__.py   # argv parsing, top-level flow, error dialogs
  ui.py         # tkinter form + simple message/error/retry dialogs
  excel.py      # workbook create/append, hyperlink, formatting
  config.py     # config.json resolution next to the exe
config.example.json
build.ps1       # PyInstaller --onefile build, run from PowerShell
requirements.txt
tests/test_excel.py  # headless smoke (runs anywhere; Tk not required)
```

## Conventions

- One workbook per project: `<exe_dir>/<sanitized_project_name>.xlsx`.
- `No.` column auto-increments by scanning column A on append.
- `Image Link` column is `openpyxl` `Hyperlink` to the absolute screenshot path.
- All Tk imports are inside `ui.py`; tests must not import `ui.py` so they run on headless CI.
- `config.py:exe_dir()` returns the PyInstaller exe folder when frozen, else the package parent.

## Running

```
pip install -r requirements.txt
pytest                                              # headless tests
python -m greenshot_to_punchlist path\to\shot.png   # full flow (needs Tk)
.\build.ps1                                         # produce dist\greenshot-to-punchlist.exe
```

## Greenshot wiring

External Command plugin → New command:
- Command: full path to `greenshot-to-punchlist.exe`
- Argument: `"{0}"` (Greenshot substitutes the saved screenshot path)
- Capture stdout/stderr: off

## Out of scope (deferred)

- Tray icon / "View Punchlist" launcher.
- Native Navisworks plugin (would let us also capture viewpoint name, selection, model file in the row without the user typing it).
- Pre-seeded project list shipped in repo — `config.example.json` is a stub on purpose.

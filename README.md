# greenshot-to-punchlist

Tiny Windows companion for [Greenshot](https://getgreenshot.org/). After every screenshot, a 5-field form pops up; on submit, a new row is appended to a per-project `.xlsx` punchlist with a clickable hyperlink back to the image. Built so you can stay in Navisworks (or any review tool) instead of context-switching into Excel after every issue.

## What you get

- A standalone `.exe` (no Python install needed on the user's machine).
- A modal form with: Project, Discipline, Issue, Priority, Assigned To, Status.
- One `.xlsx` per project, sitting next to the exe, with auto-incrementing issue numbers and clickable image hyperlinks.
- A `config.json` you edit to set your project list, default disciplines/priorities, and assignee shortlist.

## Install

1. Build the exe (one-time, on a Windows machine with Python 3.10+):
   ```powershell
   git clone <this repo>
   cd greenshot-to-punchlist
   .\build.ps1
   ```
   This produces `dist\greenshot-to-punchlist.exe`.

2. Pick a permanent home for the tool, e.g. `C:\Tools\Punchlist\`. Copy into it:
   - `dist\greenshot-to-punchlist.exe`
   - `config.example.json` — rename to `config.json` and edit the `projects` list. Per-project workbooks will be created in this same folder on first use.

## Wire it into Greenshot

1. Greenshot tray icon → **Preferences** → **Plugins** → select **External command Plugin** → **Configure**.
2. **New** command:
   - **Name**: `Punchlist`
   - **Command**: full path to `greenshot-to-punchlist.exe` (e.g. `C:\Tools\Punchlist\greenshot-to-punchlist.exe`)
   - **Argument**: `"{0}"` (the quotes matter — paths can contain spaces)
   - **Capture stdout** / **Capture stderr**: both off
3. **OK** out.
4. Use it: take a screenshot. From Greenshot's destination picker, choose **Punchlist**. Or set it as the default destination so the form opens automatically every time.

## Daily flow

1. Find an issue in Navisworks → `PrtScn` (or your Greenshot hotkey).
2. Greenshot saves the PNG and launches the Punchlist tool.
3. The form pops up:
   - Project (combobox, from `config.json`)
   - Discipline (ARCH / STRUCT / MECH / ELEC / CIVIL)
   - Issue description
   - Priority (High / Medium / Low)
   - Assigned To
   - Status (default: Open)
4. **Submit** (Enter) → new row in `<project>.xlsx`. The `Image Link` cell is a clickable hyperlink to the screenshot.
5. Back in Navisworks, no app-switching.

Keyboard: **Enter** submits, **Esc** cancels.

## Files

- `<install_dir>\greenshot-to-punchlist.exe` — the tool.
- `<install_dir>\config.json` — your config (edit me).
- `<install_dir>\<Project Name>.xlsx` — generated on first capture per project. Project names with `\ / : * ? " < > |` are sanitized to `_` for the filename.

## Config reference

```json
{
  "workbook_dir": "",
  "projects": ["Project Alpha", "Project Beta"],
  "disciplines": ["ARCH", "STRUCT", "MECH", "ELEC", "CIVIL"],
  "priorities": ["High", "Medium", "Low"],
  "assignees": ["J. Smith", "K. Lee"]
}
```

- `workbook_dir`: blank = same folder as the exe. Set to a network path (e.g. `\\\\fileserver\\projects\\punchlists`) to share workbooks across the team.
- `projects` / `assignees`: editable freeform comboboxes — typing a new value works too.

## Develop

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pytest                                                # headless tests
python -m greenshot_to_punchlist "C:\path\to\shot.png"  # try the full flow
.\build.ps1                                           # produce the exe
```

## Troubleshooting

- **"Could not write to: ... It looks like the workbook is open in Excel."** — Close the workbook in Excel and click Retry. Excel takes an exclusive lock while open.
- **Form doesn't appear after a Greenshot capture** — Check that the External Command plugin's argument is `"{0}"` with quotes, and that you picked Punchlist as the destination (or set it as default).
- **"No config.json was found"** — On first run the tool writes `config.example.json` next to the exe. Rename to `config.json` and edit the projects list.

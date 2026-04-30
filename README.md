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

This sets things up so **every capture opens Greenshot's editor first** — you annotate (arrows, text, redaction), then send the annotated image to Punchlist. The hyperlink in the workbook points at the version with your markup.

### 1. Register Punchlist as an External Command

1. Greenshot tray icon → **Preferences** → **Plugins** → select **External command Plugin** → **Configure**.
2. **New** command:
   - **Name**: `Punchlist`
   - **Command**: full path to `greenshot-to-punchlist.exe` (e.g. `C:\Tools\Punchlist\greenshot-to-punchlist.exe`)
   - **Argument**: `"{0}"` (the quotes matter — paths can contain spaces)
   - **Capture stdout** / **Capture stderr**: both off
3. **OK** out.

### 2. Make the editor the only destination

1. Greenshot tray icon → **Preferences** → **Destination** tab.
2. Under "Select destination", **uncheck everything except** **Open in image editor**.
3. Click **OK**.

Now every capture opens Greenshot's editor automatically.

### 3. Set a real save location

The editor needs to save to disk before the path can be handed to Punchlist.

1. Preferences → **Output** tab.
2. Set **Storage location** to a real folder (e.g. `%USERPROFILE%\Pictures\Greenshot`).
3. Set **Filename pattern** to something like `%YYYY%-%MM%-%DD%_%HH%-%mm%-%ss%`.

### Daily use

1. Take a screenshot → Greenshot's editor opens.
2. Annotate.
3. In the editor toolbar, click the destination dropdown (or **File** menu) → pick **Punchlist**.
4. The Punchlist form pops up with the path to the annotated image. Fill it in, **Submit**.

## Punchlist form

When the form pops up:
- Project (combobox, from `config.json`)
- Discipline (ARCH / STRUCT / MECH / ELEC / CIVIL)
- Title (short, single-line — shown in the register's Title column for quick scanning)
- Description (multi-line)
- Priority (High / Medium / Low)
- Assigned To
- Status (default: Open)

**Submit** (Enter) → new row in `<project>.xlsx` with an embedded thumbnail of the annotated screenshot in the Preview column.

Keyboard: **Enter** submits, **Esc** cancels.

## What the workbook looks like

Columns: `No., Date, Project, Discipline, Title, Description, Priority, Assigned To, Status, Screenshot, Preview`.

- **AutoFilter** is enabled on the header — click the dropdowns to filter by Discipline, Priority, Status, etc.
- **Date** is a real Excel date (formatted `yyyy-mm-dd`), so chronological sort and "last 7 days" filters work.
- **Discipline / Priority / Status** are dropdowns (data validation) so future rows stay clean.
- **Preview** is an embedded thumbnail (~145×75 px) of the annotated PNG. The full-resolution file lives in your Greenshot output folder; the **Screenshot** column has the filename so you can find it.
- Header row is frozen.

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

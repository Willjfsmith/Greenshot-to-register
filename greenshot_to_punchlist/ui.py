"""tkinter form for capturing a punchlist entry."""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

from .config import Config


@dataclass
class FormResult:
    project: str
    discipline: str
    title: str
    description: str
    priority: str
    assigned_to: str
    status: str


def show_form(cfg: Config, screenshot_path: Path) -> FormResult | None:
    """Open the modal form. Returns FormResult on submit, None on cancel."""
    root = tk.Tk()
    root.title("Add to Punchlist")
    root.attributes("-topmost", True)
    root.resizable(False, False)

    result: dict[str, FormResult | None] = {"value": None}

    pad = {"padx": 8, "pady": 4}
    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frame, text=f"Screenshot: {screenshot_path.name}").grid(
        row=0, column=0, columnspan=2, sticky="w", **pad
    )

    ttk.Label(frame, text="Project").grid(row=1, column=0, sticky="e", **pad)
    project_var = tk.StringVar(value=cfg.projects[0] if cfg.projects else "")
    project_cb = ttk.Combobox(
        frame, textvariable=project_var, values=cfg.projects, width=38
    )
    project_cb.grid(row=1, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Discipline").grid(row=2, column=0, sticky="e", **pad)
    discipline_var = tk.StringVar(value=cfg.disciplines[0] if cfg.disciplines else "")
    discipline_cb = ttk.Combobox(
        frame,
        textvariable=discipline_var,
        values=cfg.disciplines,
        width=38,
        state="readonly",
    )
    discipline_cb.grid(row=2, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Title").grid(row=3, column=0, sticky="e", **pad)
    title_var = tk.StringVar()
    title_entry = ttk.Entry(frame, textvariable=title_var, width=40)
    title_entry.grid(row=3, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Description").grid(row=4, column=0, sticky="ne", **pad)
    description_text = tk.Text(frame, width=42, height=5, wrap="word")
    description_text.grid(row=4, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Priority").grid(row=5, column=0, sticky="e", **pad)
    default_priority = "Medium" if "Medium" in cfg.priorities else (
        cfg.priorities[0] if cfg.priorities else ""
    )
    priority_var = tk.StringVar(value=default_priority)
    priority_cb = ttk.Combobox(
        frame,
        textvariable=priority_var,
        values=cfg.priorities,
        width=38,
        state="readonly",
    )
    priority_cb.grid(row=5, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Assigned To").grid(row=6, column=0, sticky="e", **pad)
    assigned_var = tk.StringVar()
    assigned_cb = ttk.Combobox(
        frame, textvariable=assigned_var, values=cfg.assignees, width=38
    )
    assigned_cb.grid(row=6, column=1, sticky="we", **pad)

    ttk.Label(frame, text="Status").grid(row=7, column=0, sticky="e", **pad)
    status_var = tk.StringVar(value="Open")
    status_cb = ttk.Combobox(
        frame,
        textvariable=status_var,
        values=["Open", "In Progress", "Resolved", "Closed"],
        width=38,
    )
    status_cb.grid(row=7, column=1, sticky="we", **pad)

    error_var = tk.StringVar(value="")
    error_label = ttk.Label(frame, textvariable=error_var, foreground="#B00020")
    error_label.grid(row=8, column=0, columnspan=2, sticky="w", **pad)

    def on_submit(event: tk.Event | None = None) -> None:
        project = project_var.get().strip()
        title = title_var.get().strip()
        description = description_text.get("1.0", "end").strip()
        if not project:
            error_var.set("Project is required.")
            project_cb.focus_set()
            return
        if not title:
            error_var.set("Title is required.")
            title_entry.focus_set()
            return
        result["value"] = FormResult(
            project=project,
            discipline=discipline_var.get().strip(),
            title=title,
            description=description,
            priority=priority_var.get().strip(),
            assigned_to=assigned_var.get().strip(),
            status=status_var.get().strip() or "Open",
        )
        root.destroy()

    def on_cancel(event: tk.Event | None = None) -> None:
        result["value"] = None
        root.destroy()

    button_row = ttk.Frame(frame)
    button_row.grid(row=9, column=0, columnspan=2, sticky="e", **pad)
    ttk.Button(button_row, text="Cancel", command=on_cancel).grid(row=0, column=0, padx=4)
    ttk.Button(button_row, text="Submit", command=on_submit).grid(row=0, column=1, padx=4)

    root.bind("<Return>", on_submit)
    root.bind("<Escape>", on_cancel)
    root.protocol("WM_DELETE_WINDOW", on_cancel)

    project_cb.focus_set()
    root.update_idletasks()
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 3
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()
    return result["value"]


def show_message(title: str, message: str) -> None:
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, message)
    root.destroy()


def show_error(title: str, message: str) -> None:
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showerror(title, message)
    root.destroy()


def ask_retry(title: str, message: str) -> bool:
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    answer = messagebox.askretrycancel(title, message)
    root.destroy()
    return bool(answer)

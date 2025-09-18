from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional


class SystemSkill:
    def __init__(self):
        self.desktop = Path.home() / "Desktop"

    def launch_app(self, name: str) -> str:
        if not name:
            return "Which app?"
        n = name.lower().strip()
        mapping = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "command prompt": "cmd.exe",
            "powershell": "powershell.exe",
            "edge": "msedge.exe",
            "chrome": "chrome.exe",
        }
        exe = mapping.get(n)
        if exe:
            try:
                subprocess.Popen([exe], shell=True)
                return f"Opening {n}."
            except Exception as e:
                return f"Failed to open {n}: {e}"
        try:
            subprocess.Popen(["start", "", name], shell=True)
            return f"Starting {name}."
        except Exception as e:
            return f"Couldn't start {name}: {e}"

    def create_folder(self, name: str, parent: Optional[Path] = None) -> str:
        if not name:
            return "Folder name?"
        parent = parent or self.desktop
        path = parent / name
        try:
            path.mkdir(parents=True, exist_ok=True)
            return f"Created folder {path.name} on {parent.name}."
        except Exception as e:
            return f"Failed to create folder: {e}"

    def delete_path(self, target: str, base: Optional[Path] = None) -> str:
        if not target:
            return "What should I delete?"
        base = base or self.desktop
        path = (base / target).expanduser()
        try:
            if path.is_dir():
                for p in sorted(path.rglob("*"), reverse=True):
                    if p.is_file():
                        p.unlink(missing_ok=True)  # type: ignore[arg-type]
                    else:
                        p.rmdir()
                path.rmdir()
                return f"Deleted folder {path.name}."
            elif path.is_file():
                path.unlink(missing_ok=True)  # type: ignore[arg-type]
                return f"Deleted file {path.name}."
            else:
                return f"Path not found: {path}"
        except Exception as e:
            return f"Failed to delete: {e}"

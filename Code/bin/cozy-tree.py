#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# bin/cozy-tree.py
# Built using a single shared braincell by Yours Truly and Grok

"""CozyTree — Beautiful, clean project tree that respects .gitignore.
Shows tree from wherever you run it, but still uses the project's .gitignore.
"""

import os
import fnmatch
from pathlib import Path


class CozyTree:
    """Gentle, reusable class for printing a cozy, filtered project tree."""

    def __init__(self, start_path: str = "."):
        self.root = Path(start_path).resolve()          # where you ran it
        self.project_root = self._find_project_root(self.root)
        self.gitignore_patterns = self._load_gitignore_patterns()

    def _find_project_root(self, start: Path) -> Path:
        current = start
        while current != current.parent:
            if (current / ".gitignore").exists():
                return current
            current = current.parent
        return start

    def _load_gitignore_patterns(self) -> list[str]:
        gitignore = self.project_root / ".gitignore"
        if not gitignore.exists():
            return []
        patterns = []
        try:
            with open(gitignore, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line.rstrip("/").strip())
        except Exception:
            pass
        return patterns

    def _should_ignore(self, rel_path: str) -> bool:
        """Now properly handles wildcards like *.log, *.pyc, etc."""
        if not rel_path or rel_path == ".":
            return False

        # Check both full relative path and just the filename
        for pattern in self.gitignore_patterns:
            if (fnmatch.fnmatch(rel_path, pattern) or
                fnmatch.fnmatch(os.path.basename(rel_path), pattern)):
                return True
        return False

    def print(self):
        print("✨ Cozy clean tree (respecting .gitignore + no empty folders) 🌱")
        print(f"Showing from: {self.root}\n")

        for dirpath, dirnames, filenames in os.walk(self.root):
            rel_dir = os.path.relpath(dirpath, self.root)
            if rel_dir == ".":
                rel_dir = ""

            if self._should_ignore(rel_dir) or "__pycache__" in dirpath:
                dirnames[:] = []
                continue

            visible_files = [
                f for f in filenames
                if not f.endswith((".pyc", ".pyo", ".pyd"))
                and not self._should_ignore(os.path.join(rel_dir, f) if rel_dir else f)
            ]

            visible_subdirs = [
                d for d in dirnames
                if not self._should_ignore(os.path.join(rel_dir, d))
            ]

            if rel_dir and not visible_files and not visible_subdirs:
                dirnames[:] = []
                continue

            level = rel_dir.count(os.sep)
            indent = "    " * level

            if rel_dir:
                print(f"{indent}├── 📁 {os.path.basename(dirpath)}")

            subindent = "    " * (level + 1)
            for f in sorted(visible_files):
                print(f"{subindent}├── 📄 {f}")


if __name__ == "__main__":
    CozyTree().print()
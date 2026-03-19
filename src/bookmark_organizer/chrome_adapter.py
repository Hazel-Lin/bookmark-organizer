from __future__ import annotations

import json
import platform
import shutil
from pathlib import Path
from typing import Iterable

from .utils import now_chrome_timestamp


class ChromeAdapter:
    def __init__(self, browser: str = "chrome", profile: str = "Default", bookmarks_path: str | None = None):
        self.browser = browser
        self.profile = profile
        self.bookmarks_path = Path(bookmarks_path) if bookmarks_path else self._default_bookmarks_path()

    def _default_bookmarks_path(self) -> Path:
        system = platform.system()
        if system == "Darwin":
            return Path.home() / "Library/Application Support/Google/Chrome" / self.profile / "Bookmarks"
        if system == "Windows":
            base = Path.home() / "AppData/Local/Google/Chrome/User Data"
            return base / self.profile / "Bookmarks"
        return Path.home() / ".config/google-chrome" / self.profile / "Bookmarks"

    def load(self) -> dict:
        with self.bookmarks_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict) -> None:
        with self.bookmarks_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    def backup(self, backup_dir: Path) -> Path:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"Bookmarks.backup.{now_chrome_timestamp()}"
        shutil.copy2(self.bookmarks_path, backup_path)
        return backup_path

    def roots(self, data: dict) -> Iterable[dict]:
        roots = data.get("roots", {})
        for key in ("bookmark_bar", "other", "synced"):
            root = roots.get(key)
            if isinstance(root, dict):
                yield root

    def find_by_id(self, data: dict, node_id: str) -> dict | None:
        for root in self.roots(data):
            found = self._find_by_id(root, node_id)
            if found:
                return found
        return None

    def find_by_name(self, data: dict, name: str) -> dict | None:
        for root in self.roots(data):
            found = self._find_by_name(root, name)
            if found:
                return found
        return None

    def list_top_level_folders(self, data: dict) -> list[dict]:
        results: list[dict] = []
        for root in self.roots(data):
            for child in root.get("children", []) or []:
                if child.get("type") == "folder":
                    results.append(
                        {
                            "root": root.get("name"),
                            "id": child.get("id"),
                            "name": child.get("name"),
                            "bookmark_count": self.count_urls(child),
                            "child_folder_count": sum(
                                1 for grandchild in child.get("children", []) or [] if grandchild.get("type") == "folder"
                            ),
                        }
                    )
        return results

    def count_urls(self, node: dict) -> int:
        total = 1 if node.get("type") == "url" else 0
        for child in node.get("children", []) or []:
            total += self.count_urls(child)
        return total

    def _find_by_id(self, node: dict, node_id: str) -> dict | None:
        if node.get("id") == node_id:
            return node
        for child in node.get("children", []) or []:
            found = self._find_by_id(child, node_id)
            if found:
                return found
        return None

    def _find_by_name(self, node: dict, name: str) -> dict | None:
        if node.get("name") == name:
            return node
        for child in node.get("children", []) or []:
            found = self._find_by_name(child, name)
            if found:
                return found
        return None


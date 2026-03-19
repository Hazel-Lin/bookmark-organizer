from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BookmarkItem:
    id: str
    name: str
    url: str
    path: str
    source_folder_id: str
    source_folder_name: str
    raw_node: dict[str, Any]
    score_debug: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class FolderSpec:
    id: str
    name: str


@dataclass
class FolderSummary:
    id: str
    name: str
    bookmark_count: int
    child_folder_count: int

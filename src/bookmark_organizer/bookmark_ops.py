from __future__ import annotations

from typing import Iterable

from .models import BookmarkItem


def flatten_folder(node: dict, parent_path: list[str] | None = None, source_folder: dict | None = None) -> list[BookmarkItem]:
    parent_path = parent_path or []
    source_folder = source_folder or node
    rows: list[BookmarkItem] = []
    if node.get("type") == "url":
        rows.append(
            BookmarkItem(
                id=node["id"],
                name=node.get("name", ""),
                url=node.get("url", ""),
                path=" / ".join(part for part in parent_path if part),
                source_folder_id=source_folder.get("id", ""),
                source_folder_name=source_folder.get("name", ""),
                raw_node=node,
            )
        )
        return rows
    current_path = parent_path + [node.get("name", "")]
    next_source = source_folder if source_folder is not None and source_folder.get("id") else node
    for child in node.get("children", []) or []:
        rows.extend(flatten_folder(child, current_path, next_source))
    return rows


def collect_ids(items: Iterable[BookmarkItem]) -> set[str]:
    return {item.id for item in items}


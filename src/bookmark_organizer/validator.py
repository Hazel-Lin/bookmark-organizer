from __future__ import annotations

from typing import Iterable

from .chrome_adapter import ChromeAdapter


ROOT_BUCKET_ID = "__root__"
ROOT_BUCKET_NAME = "(root)"


def collect_urls(node: dict, out: dict[str, dict]) -> None:
    if node.get("type") == "url" and node.get("id"):
        out[node["id"]] = node
    for child in node.get("children", []) or []:
        if isinstance(child, dict):
            collect_urls(child, out)


def collect_urls_for_top_level(node: dict, bucket_id: str, bucket_name: str, out: dict[str, dict[str, str]]) -> None:
    if node.get("type") == "url" and node.get("id"):
        out[node["id"]] = {"folder_id": bucket_id, "folder_name": bucket_name}
        return
    for child in node.get("children", []) or []:
        if isinstance(child, dict):
            collect_urls_for_top_level(child, bucket_id, bucket_name, out)


def current_top_level_assignments(root: dict) -> dict[str, dict[str, str]]:
    assignments: dict[str, dict[str, str]] = {}
    for child in root.get("children", []) or []:
        if not isinstance(child, dict):
            continue
        if child.get("type") == "folder":
            collect_urls_for_top_level(
                child,
                bucket_id=child.get("id", ""),
                bucket_name=child.get("name", ""),
                out=assignments,
            )
        elif child.get("type") == "url" and child.get("id"):
            assignments[child["id"]] = {"folder_id": ROOT_BUCKET_ID, "folder_name": ROOT_BUCKET_NAME}
    return assignments


def _duplicate_ids(bookmark_ids: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for bookmark_id in bookmark_ids:
        if bookmark_id in seen:
            duplicates.add(bookmark_id)
        seen.add(bookmark_id)
    return sorted(duplicates, key=_sort_key)


def _sort_key(value: str) -> tuple[int, str]:
    return (0, value) if value.isdigit() else (1, value)


def validate_plan(adapter: ChromeAdapter, root_id: str, plan_data: dict) -> dict:
    data = adapter.load()
    root = adapter.find_by_id(data, root_id)
    if not root:
        raise RuntimeError(f"Root folder {root_id} not found")

    folder_specs = plan_data.get("folder_specs", [])
    plan = plan_data.get("plan", {})
    planned_ids = [bookmark_id for ids in plan.values() for bookmark_id in ids]
    duplicate_bookmark_ids = _duplicate_ids(planned_ids)

    folder_ids = [spec["id"] for spec in folder_specs]
    duplicate_folder_ids = _duplicate_ids(folder_ids)
    unknown_plan_folders = sorted(folder_id for folder_id in plan if folder_id not in set(folder_ids))

    all_urls: dict[str, dict] = {}
    collect_urls(root, all_urls)
    actual_set = set(all_urls)
    planned_set = set(planned_ids)
    missing_bookmark_ids = sorted(planned_set - actual_set, key=_sort_key)
    unmapped_bookmark_ids = sorted(actual_set - planned_set, key=_sort_key)

    return {
        "valid": not any(
            [
                duplicate_bookmark_ids,
                duplicate_folder_ids,
                unknown_plan_folders,
                missing_bookmark_ids,
                unmapped_bookmark_ids,
            ]
        ),
        "target": {"id": root_id, "name": root.get("name")},
        "summary": {
            "bookmark_count": len(all_urls),
            "planned_bookmark_count": len(planned_ids),
            "folder_count": len(folder_specs),
        },
        "issues": {
            "duplicate_bookmark_ids": duplicate_bookmark_ids,
            "duplicate_folder_ids": duplicate_folder_ids,
            "unknown_plan_folders": unknown_plan_folders,
            "missing_bookmark_ids": missing_bookmark_ids,
            "unmapped_bookmark_ids": unmapped_bookmark_ids,
        },
    }


def diff_plan(adapter: ChromeAdapter, root_id: str, plan_data: dict) -> dict:
    data = adapter.load()
    root = adapter.find_by_id(data, root_id)
    if not root:
        raise RuntimeError(f"Root folder {root_id} not found")

    validation = validate_plan(adapter, root_id, plan_data)
    folder_name_by_id = {spec["id"]: spec["name"] for spec in plan_data.get("folder_specs", [])}
    current_assignments = current_top_level_assignments(root)

    all_urls: dict[str, dict] = {}
    collect_urls(root, all_urls)

    changes: list[dict] = []
    unchanged_count = 0
    for folder_id, bookmark_ids in plan_data.get("plan", {}).items():
        planned_name = folder_name_by_id.get(folder_id, folder_id)
        for bookmark_id in bookmark_ids:
            item = all_urls.get(bookmark_id)
            if item is None:
                continue
            current = current_assignments.get(
                bookmark_id,
                {"folder_id": ROOT_BUCKET_ID, "folder_name": ROOT_BUCKET_NAME},
            )
            if current["folder_id"] == folder_id:
                unchanged_count += 1
                continue
            changes.append(
                {
                    "bookmark_id": bookmark_id,
                    "bookmark_name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "from": current,
                    "to": {"folder_id": folder_id, "folder_name": planned_name},
                }
            )

    return {
        "target": {"id": root_id, "name": root.get("name")},
        "summary": {
            "change_count": len(changes),
            "unchanged_count": unchanged_count,
        },
        "validation": validation,
        "changes": changes,
    }

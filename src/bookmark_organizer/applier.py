from __future__ import annotations

from .chrome_adapter import ChromeAdapter
from .utils import is_chrome_running, new_guid, now_chrome_timestamp


def collect_urls(node: dict, out: dict[str, dict]) -> None:
    if node.get("type") == "url" and node.get("id"):
        out[node["id"]] = node
    for child in node.get("children", []) or []:
        if isinstance(child, dict):
            collect_urls(child, out)


def apply_plan(adapter: ChromeAdapter, root_id: str, plan_data: dict, allow_unmapped: bool = False) -> dict:
    if is_chrome_running():
        raise RuntimeError("Google Chrome is running. Close Chrome before apply.")

    data = adapter.load()
    root = adapter.find_by_id(data, root_id)
    if not root:
        raise RuntimeError(f"Root folder {root_id} not found")

    folder_specs = plan_data["folder_specs"]
    plan = plan_data["plan"]

    existing_children = root.get("children", [])
    child_map = {child["id"]: child for child in existing_children if isinstance(child, dict) and child.get("id")}
    all_urls: dict[str, dict] = {}
    for child in existing_children:
        if isinstance(child, dict):
            collect_urls(child, all_urls)

    planned_set = {bookmark_id for ids in plan.values() for bookmark_id in ids}
    actual_set = set(all_urls)
    missing = sorted(planned_set - actual_set)
    extra = sorted(actual_set - planned_set)
    if missing:
        raise RuntimeError(f"Plan references missing bookmark ids: {missing}")
    if extra and not allow_unmapped:
        raise RuntimeError(f"Plan does not cover current bookmark ids: {extra}")

    new_children: list[dict] = []
    for spec in folder_specs:
        folder_id = spec["id"]
        folder_name = spec["name"]
        folder = child_map.get(folder_id)
        if folder is None or folder.get("type") != "folder":
            folder = {
                "children": [],
                "date_added": now_chrome_timestamp(),
                "date_last_used": "0",
                "date_modified": now_chrome_timestamp(),
                "guid": new_guid(),
                "id": folder_id,
                "name": folder_name,
                "type": "folder",
            }
        folder["name"] = folder_name
        folder["type"] = "folder"
        folder["children"] = [all_urls[bookmark_id] for bookmark_id in plan.get(folder_id, [])]
        folder["date_modified"] = now_chrome_timestamp()
        new_children.append(folder)

    if allow_unmapped:
        for bookmark_id in sorted(extra, key=int):
            new_children.append(all_urls[bookmark_id])

    root["children"] = new_children
    root["date_modified"] = now_chrome_timestamp()
    adapter.save(data)
    return {
        "root_id": root_id,
        "root_name": root.get("name"),
        "folder_count": len(folder_specs),
        "bookmark_count": adapter.count_urls(root),
    }


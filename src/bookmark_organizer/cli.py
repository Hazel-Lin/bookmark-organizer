from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .applier import apply_plan
from .bookmark_ops import flatten_folder
from .chrome_adapter import ChromeAdapter
from .planner import classify_items
from .taxonomy import load_taxonomy
from .utils import json_dump, utc_now_iso
from .validator import diff_plan, validate_plan


def resolve_target(adapter: ChromeAdapter, data: dict, root_id: str | None, root_name: str | None) -> dict:
    if root_id:
        node = adapter.find_by_id(data, root_id)
    elif root_name:
        node = adapter.find_by_name(data, root_name)
    else:
        raise SystemExit("Provide --root-id or --root-name")
    if not node:
        raise SystemExit("Target folder not found")
    return node


def cmd_scan(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    data = adapter.load()
    results = {
        "bookmarks_path": str(adapter.bookmarks_path),
        "folders": adapter.list_top_level_folders(data),
    }
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    data = adapter.load()
    target = resolve_target(adapter, data, args.root_id, args.root_name)
    items = flatten_folder(target, [])
    results = {
        "root_id": target.get("id"),
        "root_name": target.get("name"),
        "bookmark_count": len(items),
        "items": [
            {"id": item.id, "name": item.name, "url": item.url, "path": item.path}
            for item in items
        ],
    }
    if args.output:
        json_dump(results, Path(args.output))
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    data = adapter.load()
    target = resolve_target(adapter, data, args.root_id, args.root_name)
    items = flatten_folder(target, [])
    taxonomy = load_taxonomy(args.taxonomy)
    planned = classify_items(items, taxonomy)
    output = {
        "target": {"id": target.get("id"), "name": target.get("name")},
        "metadata": {
            "generated_at": utc_now_iso(),
            "generator": "bookmark-organizer",
            "generator_version": "0.1.0",
            "profile": args.profile,
            "bookmarks_path": str(adapter.bookmarks_path),
            "taxonomy_name": taxonomy.get("name", "unnamed-taxonomy"),
            "taxonomy_source": args.taxonomy or "builtin:default",
        },
        "folder_specs": planned["folder_specs"],
        "plan": planned["plan"],
        "debug": planned["debug"] if args.include_debug else None,
        "bookmark_count": len(items),
    }
    if output["debug"] is None:
        del output["debug"]
    if args.output:
        json_dump(output, Path(args.output))
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    with Path(args.plan_file).open("r", encoding="utf-8") as f:
        plan_data = json.load(f)
    backup_path = adapter.backup(Path(args.backup_dir))
    result = apply_plan(
        adapter=adapter,
        root_id=args.root_id or plan_data["target"]["id"],
        plan_data=plan_data,
        allow_unmapped=args.allow_unmapped,
    )
    result["backup_path"] = str(backup_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    with Path(args.plan_file).open("r", encoding="utf-8") as f:
        plan_data = json.load(f)
    result = validate_plan(
        adapter=adapter,
        root_id=args.root_id or plan_data["target"]["id"],
        plan_data=plan_data,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    adapter = ChromeAdapter(profile=args.profile, bookmarks_path=args.bookmarks_path)
    with Path(args.plan_file).open("r", encoding="utf-8") as f:
        plan_data = json.load(f)
    result = diff_plan(
        adapter=adapter,
        root_id=args.root_id or plan_data["target"]["id"],
        plan_data=plan_data,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bookmark-organizer")
    parser.add_argument("--profile", default="Default")
    parser.add_argument("--bookmarks-path")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="List top-level folders and counts")
    scan.set_defaults(func=cmd_scan)

    analyze = subparsers.add_parser("analyze", help="Flatten a target folder into raw bookmark items")
    analyze.add_argument("--root-id")
    analyze.add_argument("--root-name")
    analyze.add_argument("--output")
    analyze.set_defaults(func=cmd_analyze)

    plan = subparsers.add_parser("plan", help="Generate a classification plan for a target folder")
    plan.add_argument("--root-id")
    plan.add_argument("--root-name")
    plan.add_argument("--taxonomy")
    plan.add_argument("--output")
    plan.add_argument("--include-debug", action="store_true")
    plan.set_defaults(func=cmd_plan)

    apply = subparsers.add_parser("apply", help="Apply a plan file to a target folder")
    apply.add_argument("--root-id")
    apply.add_argument("--plan-file", required=True)
    apply.add_argument("--backup-dir", default=str(Path.home() / "Desktop/chrome-bookmark-audit/output/backups"))
    apply.add_argument("--allow-unmapped", action="store_true")
    apply.set_defaults(func=cmd_apply)

    validate = subparsers.add_parser("validate", help="Validate a plan file against the current bookmark state")
    validate.add_argument("--root-id")
    validate.add_argument("--plan-file", required=True)
    validate.set_defaults(func=cmd_validate)

    diff = subparsers.add_parser("diff", help="Show bookmark moves implied by a plan file")
    diff.add_argument("--root-id")
    diff.add_argument("--plan-file", required=True)
    diff.set_defaults(func=cmd_diff)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

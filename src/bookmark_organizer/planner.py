from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlparse

from .models import BookmarkItem


def normalize_host(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def classify_items(items: list[BookmarkItem], taxonomy: dict) -> dict:
    folder_specs = taxonomy["folder_specs"]
    rules = taxonomy["rules"]
    fallback_folder_id = taxonomy["fallback_folder_id"]
    by_folder: dict[str, list[str]] = defaultdict(list)
    debug: dict[str, dict[str, list[str]]] = {}

    for item in items:
        haystack = f"{item.name} {item.url} {item.path}".lower()
        host = normalize_host(item.url)
        best_folder_id = fallback_folder_id
        best_score = -1
        reasons: list[str] = []
        for rule in rules:
            score = 0
            current_reasons: list[str] = []
            for keyword in rule.get("keywords", []):
                if keyword.lower() in haystack:
                    score += 2
                    current_reasons.append(f"keyword:{keyword}")
            for allowed_host in rule.get("hosts", []):
                if host == allowed_host or host.endswith(f".{allowed_host}"):
                    score += 4
                    current_reasons.append(f"host:{allowed_host}")
            if score > best_score:
                best_score = score
                best_folder_id = rule["folder_id"]
                reasons = current_reasons
        by_folder[best_folder_id].append(item.id)
        debug[item.id] = {"folder_id": best_folder_id, "reasons": reasons}

    return {
        "folder_specs": folder_specs,
        "plan": {spec["id"]: by_folder.get(spec["id"], []) for spec in folder_specs},
        "debug": debug,
    }


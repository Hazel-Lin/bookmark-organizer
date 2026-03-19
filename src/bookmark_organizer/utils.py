from __future__ import annotations

import json
import platform
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def now_chrome_timestamp() -> str:
    return str(int((time.time() + 11644473600) * 1_000_000))


def new_guid() -> str:
    return str(uuid.uuid4())


def slugify(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "folder"


def is_chrome_running() -> bool:
    system = platform.system()
    if system == "Darwin":
        proc = subprocess.run(["pgrep", "-x", "Google Chrome"], capture_output=True, text=True)
        return proc.returncode == 0
    if system == "Windows":
        proc = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True,
            text=True,
            shell=True,
        )
        return "chrome.exe" in proc.stdout.lower()
    proc = subprocess.run(["pgrep", "-x", "chrome"], capture_output=True, text=True)
    return proc.returncode == 0


def json_dump(data: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

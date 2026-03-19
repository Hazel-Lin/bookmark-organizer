from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bookmark_organizer.models import BookmarkItem
from bookmark_organizer.planner import classify_items, normalize_host
from bookmark_organizer.taxonomy import DEFAULT_TAXONOMY


class PlannerTests(unittest.TestCase):
    def test_normalize_host_removes_www_prefix(self) -> None:
        self.assertEqual(normalize_host("https://www.example.com/docs"), "example.com")

    def test_classify_items_uses_taxonomy_rules(self) -> None:
        items = [
            BookmarkItem(
                id="49",
                name="Ahrefs Guide",
                url="https://ahrefs.com/blog",
                path="AI 出海",
                source_folder_id="166",
                source_folder_name="AI 出海",
                raw_node={},
            ),
            BookmarkItem(
                id="50",
                name="LangChain Docs",
                url="https://python.langchain.com/",
                path="AI 出海",
                source_folder_id="166",
                source_folder_name="AI 出海",
                raw_node={},
            ),
        ]

        planned = classify_items(items, DEFAULT_TAXONOMY)

        self.assertEqual(planned["plan"]["cat-01"], ["49"])
        self.assertEqual(planned["plan"]["cat-03"], ["50"])


if __name__ == "__main__":
    unittest.main()

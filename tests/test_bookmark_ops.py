from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bookmark_organizer.bookmark_ops import flatten_folder


class FlattenFolderTests(unittest.TestCase):
    def test_flatten_folder_collects_nested_urls(self) -> None:
        root = {
            "id": "166",
            "name": "AI 出海",
            "type": "folder",
            "children": [
                {
                    "id": "200",
                    "name": "Nested",
                    "type": "folder",
                    "children": [
                        {
                            "id": "49",
                            "name": "Ahrefs Blog",
                            "type": "url",
                            "url": "https://ahrefs.com/blog",
                        }
                    ],
                },
                {
                    "id": "51",
                    "name": "Product Hunt",
                    "type": "url",
                    "url": "https://producthunt.com/",
                },
            ],
        }

        items = flatten_folder(root)

        self.assertEqual([item.id for item in items], ["49", "51"])
        self.assertEqual(items[0].path, "AI 出海 / Nested")
        self.assertEqual(items[0].source_folder_id, "166")
        self.assertEqual(items[1].path, "AI 出海")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bookmark_organizer.cli import main


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "sample-bookmarks.json"
TAXONOMY = ROOT / "examples" / "default-taxonomy.json"


class CliTests(unittest.TestCase):
    def run_cli(self, args: list[str]) -> dict:
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            exit_code = main(args)
        self.assertEqual(exit_code, 0)
        return json.loads(stdout.getvalue())

    def test_scan_lists_top_level_folders(self) -> None:
        result = self.run_cli(["--bookmarks-path", str(FIXTURE), "scan"])

        self.assertEqual(result["bookmarks_path"], str(FIXTURE))
        self.assertEqual(result["folders"][0]["name"], "AI 出海")
        self.assertEqual(result["folders"][0]["bookmark_count"], 3)

    def test_plan_generates_expected_folder_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "plan.json"
            exit_code = main(
                [
                    "--bookmarks-path",
                    str(FIXTURE),
                    "plan",
                    "--root-name",
                    "AI 出海",
                    "--taxonomy",
                    str(TAXONOMY),
                    "--output",
                    str(output_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["target"]["id"], "166")
        self.assertEqual(payload["metadata"]["taxonomy_name"], "default-startup-bookmarks")
        self.assertEqual(payload["metadata"]["taxonomy_source"], str(TAXONOMY))
        self.assertEqual(payload["plan"]["cat-01"], ["49"])
        self.assertEqual(payload["plan"]["cat-03"], ["50"])
        self.assertEqual(payload["plan"]["cat-07"], ["51"])

    def test_validate_reports_plan_as_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "plan.json"
            main(
                [
                    "--bookmarks-path",
                    str(FIXTURE),
                    "plan",
                    "--root-name",
                    "AI 出海",
                    "--taxonomy",
                    str(TAXONOMY),
                    "--output",
                    str(output_path),
                ]
            )

            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main(
                    [
                        "--bookmarks-path",
                        str(FIXTURE),
                        "validate",
                        "--plan-file",
                        str(output_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["issues"]["missing_bookmark_ids"], [])
        self.assertEqual(payload["issues"]["unmapped_bookmark_ids"], [])

    def test_diff_reports_moves_from_current_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "plan.json"
            main(
                [
                    "--bookmarks-path",
                    str(FIXTURE),
                    "plan",
                    "--root-name",
                    "AI 出海",
                    "--taxonomy",
                    str(TAXONOMY),
                    "--output",
                    str(output_path),
                ]
            )

            with patch("sys.stdout", new_callable=StringIO) as stdout:
                exit_code = main(
                    [
                        "--bookmarks-path",
                        str(FIXTURE),
                        "diff",
                        "--plan-file",
                        str(output_path),
                    ]
                )

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["summary"]["change_count"], 3)
        self.assertEqual(payload["changes"][0]["from"]["folder_name"], "Nested")
        self.assertEqual(payload["changes"][2]["from"]["folder_name"], "(root)")


if __name__ == "__main__":
    unittest.main()

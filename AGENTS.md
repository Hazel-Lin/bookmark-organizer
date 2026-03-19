# Repository Guidelines

## Project Structure & Module Organization

Core Python code lives in `src/bookmark_organizer/`. Keep CLI entrypoints in `cli.py`, browser/file adapters in `chrome_adapter.py`, planning logic in `planner.py`, and write-path safety logic in `applier.py`. Sample inputs and taxonomy files belong in `examples/`. Regression tests live in `tests/`. Repository-facing assets for documentation, such as GIFs used by the README, belong in `media/`. Local working notes can live in `docs/`, which is ignored. Marketing copy drafts stay in `marketing/` and should not affect runtime behavior.

## Build, Test, and Development Commands

- `python3 -m venv .venv && source .venv/bin/activate`: create and enter a local virtualenv.
- `pip install .`: install the package and CLI entrypoint locally.
- `PYTHONPATH=src python3 -m bookmark_organizer.cli --help`: run the CLI from source without installation.
- `python3 -m unittest discover -s tests -v`: run the full test suite.
- `python3 -m build` or `python3 -m pip install .`: verify packaging before release.

## Coding Style & Naming Conventions

Use Python 3.9+ with 4-space indentation and standard library-first solutions where practical. Prefer small, single-purpose functions and explicit JSON-friendly return shapes. Use `snake_case` for functions, modules, and variables; use `PascalCase` for dataclasses such as `BookmarkItem`. Keep CLI commands action-oriented (`scan`, `analyze`, `plan`, `apply`). Add brief comments only where the safety or data-shape logic is not obvious.

## Testing Guidelines

Tests use the standard library `unittest` framework. Name test files `test_*.py` and keep fixtures deterministic. Cover any change to planning rules, bookmark flattening, or apply safety checks with regression tests. When adding a new CLI behavior, include at least one test that exercises the command using the sample data in `examples/sample-bookmarks.json`.

## Commit & Pull Request Guidelines

This repository does not yet have meaningful Git history, so use clear Conventional Commit-style messages such as `feat: add validate command` or `docs: update Chinese README`. PRs should include a short summary, the commands used for validation, and any README or example updates required by the change. For user-facing workflow changes, include terminal output or screenshots/GIF updates when relevant.

## Security & Safety Notes

This project modifies local bookmark data. Preserve the `scan -> analyze -> plan -> apply` contract, keep backups before writes, and do not weaken Chrome-running checks or plan validation without explicit justification and tests.

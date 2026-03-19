# bookmark-organizer

[English](README.md) | [简体中文](README.zh-CN.md)

`bookmark-organizer` is a Python CLI for scanning, analyzing, planning, and safely reorganizing browser bookmarks.

It is built for an agent-friendly workflow:

- machine-readable JSON output
- deterministic `plan.json`
- backup before apply
- dry-run planning before any write

## Why

Most bookmark tools either dump everything into broad folders or require manual drag-and-drop. This project treats bookmark cleanup as an auditable workflow:

1. discover candidate folders
2. flatten the target subtree
3. classify bookmarks into a taxonomy
4. generate a reusable JSON plan
5. apply only after review

The goal is not "auto sort everything blindly". The goal is a safe `scan -> analyze -> plan -> apply` contract that another agent or human can inspect before any local data is rewritten.

![bookmark-organizer demo](media/bookmark-organizer-demo.gif)

## Features

- Chrome bookmarks file support
- macOS, Windows, and Linux path discovery for Chrome profiles
- folder-level reorganization with custom taxonomy JSON
- backup-on-write safety model
- deterministic plan generation for review and reuse

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

If you want to run from source without installing:

```bash
PYTHONPATH=src python3 -m bookmark_organizer.cli scan
```

## Quick Start

Replace `<folder-name>` and `<folder-id>` with a folder discovered by `bookmark-organizer scan`. Do not copy the placeholders literally.

List top-level folders:

```bash
bookmark-organizer scan
bookmark-organizer scan --profile Default
```

Flatten a target folder:

```bash
bookmark-organizer analyze --root-name "<folder-name>"
bookmark-organizer analyze --root-id <folder-id> --output /tmp/bookmarks.json
```

Generate a reviewable plan:

```bash
bookmark-organizer plan --root-name "<folder-name>" --output /tmp/plan.json
bookmark-organizer plan --root-name "<folder-name>" --taxonomy examples/default-taxonomy.json --include-debug
```

Validate a plan before writing:

```bash
bookmark-organizer validate --plan-file /tmp/plan.json
```

Review the intended moves:

```bash
bookmark-organizer diff --plan-file /tmp/plan.json
```

Apply a plan after review and with Chrome closed:

```bash
bookmark-organizer apply --plan-file /tmp/plan.json
```

## CLI Workflow

### `scan`

Discover candidate bookmark folders and counts.

### `analyze`

Flatten a target folder into bookmark rows so classification is based on actual content rather than old nested structure.

### `plan`

Generate a deterministic `plan.json`. This is the default dry run step and does not modify bookmarks.

### `apply`

Back up the browser bookmark file, validate the plan against current bookmark ids, and write the new folder structure.

### `validate`

Check whether a plan is still safe to apply against the current bookmark file. This catches stale plans, missing bookmark ids, duplicate assignments, and unmapped bookmarks before any write.

### `diff`

Show which bookmarks would move from the current top-level layout into the planned folders. This is the quickest review step before `apply`.

## Plan Format

```json
{
  "target": { "id": "166", "name": "Research Links" },
  "folder_specs": [
    { "id": "cat-01", "name": "01 SEO & Marketing" }
  ],
  "plan": {
    "cat-01": ["49", "196"]
  }
}
```

## Safety Model

- `scan` and `analyze` are read-only
- `plan` is read-only
- `apply` creates a backup before writing
- `apply` refuses to run while Chrome is open
- `apply` validates that the generated plan still matches current bookmark ids

## Agent Usage

Agents can treat the CLI as a four-step contract:

1. `scan` to discover candidate folders
2. `analyze` to flatten the selected target
3. `plan` to generate `plan.json`
4. `apply` only after explicit confirmation

This makes the tool safe to automate from Codex, Claude Code, or shell scripts without inventing a custom protocol.

## Project Layout

```text
src/bookmark_organizer/   core CLI and bookmark operations
examples/                 sample taxonomy and fixtures
tests/                    regression tests for planner and CLI behavior
marketing/                launch copy and distribution drafts
media/                    tracked README assets
.github/                  issue templates, PR template, and CI
```

## Development

Run the built-in test suite:

```bash
python3 -m unittest discover -s tests -v
```

Check CLI help:

```bash
PYTHONPATH=src python3 -m bookmark_organizer.cli --help
```

## Roadmap

- Edge / Brave adapters
- runtime API fallback when browser sync rewrites file changes
- duplicate detection
- dead-link checks
- interactive TUI selection

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and issue expectations.

## Security

If you find a data-loss or unsafe-write issue, see [SECURITY.md](SECURITY.md).

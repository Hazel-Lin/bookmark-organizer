# Contributing

## Scope

`bookmark-organizer` is a local-first CLI for safely reorganizing bookmark data. Changes should preserve the project's core contract:

1. discover
2. analyze
3. plan
4. apply

Any new feature should keep the workflow auditable and default to safe behavior.

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
python3 -m unittest discover -s tests -v
```

## Pull Request Guidelines

- keep changes scoped
- include or update tests for behavioral changes
- document CLI or plan format changes in `README.md`
- do not remove safety checks without a strong justification
- prefer deterministic outputs over heuristic-only behavior

## Reporting Bugs

Please include:

- OS and Python version
- browser and profile details if relevant
- exact command run
- expected behavior
- actual behavior
- whether Chrome was open or closed
- sanitized sample bookmark JSON if the issue is data-shape specific

## Feature Requests

Good feature requests explain:

- the user workflow
- where the current `scan -> analyze -> plan -> apply` contract breaks down
- what safety or auditability guarantees the change should preserve

## Release Principle

This project manipulates user data. A small safe feature is preferable to a broad unsafe feature.

# Security Policy

## Supported Versions

This repository is currently in early alpha. Security fixes will be made against the latest version on `main`.

## Reporting a Vulnerability

Please report vulnerabilities privately and avoid opening a public issue for anything that could expose user bookmark data or enable unsafe local writes.

Include:

- affected command and version
- reproduction steps
- whether the issue can cause data loss, data corruption, or unintended writes
- a sanitized sample bookmark file if needed

## High-Priority Classes

- unsafe writes to bookmark files
- missing backup behavior
- incorrect plan validation that can drop bookmarks
- path handling bugs that write outside the intended bookmark file
- race conditions when the browser is still running

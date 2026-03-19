# Agent-Native Assessment

This document maps `bookmark-organizer` against five agent-native product principles and defines the next upgrades that would move it from a solid minimum implementation to a stronger agent-native system.

## Current Verdict

`bookmark-organizer` already qualifies as a meaningful minimum practice of an agent-native tool because it exposes a safe, machine-usable protocol:

1. `scan`
2. `analyze`
3. `plan`
4. `apply`

This is stronger than a one-off script because the workflow is explicit, auditable, and composable from an external agent loop.

## Principle-by-Principle Assessment

### 1. Parity

Status: Partial

Agents can perform the core executable steps through the CLI. However, higher-level judgment still lives outside the product: choosing the target folder, reviewing plan quality, adjusting taxonomy, and deciding when unmapped bookmarks are acceptable.

### 2. Granularity

Status: Strong

This is the best-implemented principle in the project. Each command does one thing well, and the final result is produced by sequencing small, testable operations rather than by a single opaque "organize everything" action.

### 3. Composability

Status: Partial

The four-step contract is composable, but feature expansion still depends on code and taxonomy changes. A stronger agent-native version would allow more new outcomes to emerge from prompt/context changes alone.

### 4. Emergent Capability

Status: Early

The workflow pattern is transferable, but the implementation is still tightly coupled to Chrome bookmarks and rule-based classification. The system does not yet unlock many useful tasks beyond the ones explicitly designed.

### 5. Improvement Over Time

Status: Weak

The product currently does not learn from past plans, user corrections, taxonomy revisions, or failed applies. It is reliable, but mostly static.

## What Already Counts as the Minimum Practice

The current minimum practice is not "uses AI". It is:

- a stable CLI interface
- machine-readable JSON outputs
- a reviewable `plan.json`
- backup before write
- validation before apply

That is enough for an external agent to use the product safely.

## Upgrade Path

### P0: Strengthen the Existing Protocol

- Add `validate` as an explicit command for pre-apply checks without writing.
- Add a `diff` view that summarizes folder moves in human-readable form.
- Persist plan metadata such as taxonomy version, creation time, and source profile.

### P1: Improve Parity and Composability

- Add interactive target selection for humans and structured target suggestion for agents.
- Support pluggable classifiers so prompts or external models can generate candidate categorizations.
- Allow plan post-processing rules such as "keep existing folders", "cap folder size", or "never move starred domains".

### P2: Add Real Improvement Over Time

- Save accepted and rejected plans to a local history directory.
- Learn reusable host and keyword preferences from prior approvals.
- Record correction feedback so future plans can rank categories better.

### P3: Expand Emergent Capability

- Add adapters for Edge and Brave using the same protocol.
- Generalize the workflow into a browser-agnostic bookmark reorganization interface.
- Consider a second local-data domain to prove the protocol is reusable beyond bookmarks.

## Product Standard

Any future feature should preserve the repository's core contract:

- inspect before modify
- plan before apply
- backup before write
- deterministic outputs where possible
- explicit escape hatches for unsafe cases

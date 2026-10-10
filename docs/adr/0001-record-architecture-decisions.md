# ADR-0001: Record architecture decisions in docs/adr

## Status
Accepted (2026-10-09)

## Context
The project had one design document (`DESIGN.md`) that stated goals and no decisions. Choices
such as the TensorFlow Hub training script were never recorded, so nothing says why they were
made or when they stop being right. The owner works alone and returns to the project after
long gaps.

## Decision
Record each decision between real alternatives as a numbered file in `docs/adr/`, from
[TEMPLATE.md](TEMPLATE.md), with the status line `Proposed`, `Accepted`, `Superseded by
ADR-<NNNN>` or `Deprecated`. Never edit an accepted ADR's decision. Supersede it with a new
one.

## Consequences
- A reader can find why a choice was made.
- A decision costs a file. Small, reversible choices do not need one.
- A Proposed ADR marks a question the owner has not answered, and work that depends on it waits.

## References
- [docs/README.md](../README.md) workflow

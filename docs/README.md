# Documentation

This directory holds the intent, specifications and decisions for card-identifier. Code and
tests follow these documents. When code and a document disagree, the disagreement is a bug in
one of them, and an issue records which.

## Reading order

1. [intent.md](intent.md): why the project exists, who uses it, and what success means.
2. [principles.md](principles.md): the engineering rules every spec obeys.
3. [architecture.md](architecture.md): the components, the data layout and the trust boundaries.
4. [specs/](specs/): one specification per component, with numbered requirements.
5. [adr/](adr/): the decisions behind the architecture, one file each.
6. [rtm.md](rtm.md): every requirement, with the code and test that implement it.
7. [examinations/](examinations/): dated critical examinations and the findings they produced.

## Workflow

Intent drives specs, specs drive issues, issues drive pull requests, and tests close the loop.

1. **Intent.** A change starts from a stated outcome in `intent.md`. A change with no outcome
   behind it needs the outcome written first.
2. **Spec.** The behavior goes into the matching file in `specs/` as one or more
   requirements. A requirement is one sentence in EARS form, with an acceptance check.
3. **Decision.** A choice between real alternatives gets an ADR. Copy
   [adr/TEMPLATE.md](adr/TEMPLATE.md). A Proposed ADR blocks the work that depends on it.
4. **Issue.** Each issue cites the ReqIDs it implements and states acceptance criteria that
   a reviewer can run. The issue templates ask for both.
5. **Pull request.** The pull request cites the issue and the ReqIDs. It updates the spec
   and `rtm.md` in the same change when behavior moves.
6. **Test.** Every test for a requirement carries the tag `ReqID: FR-<N>` in its docstring.
   A test without a tag is allowed. A requirement without a tagged test cannot reach
   `Verified` in `rtm.md`.

## Requirement IDs

- `FR-<N>` is a functional requirement and `NFR-<N>` a non-functional one. Numbers are
  assigned once and never reused. A removed requirement keeps its number, marked `Withdrawn`.
- Blocks: catalog 100s, generation 200s, selection 300s, training 400s, evaluation 500s,
  inference 600s. Cross-cutting NFR numbers 1 to 99 live in [specs/nfr.md](specs/nfr.md).
- EARS patterns used: `WHEN <event> THE SYSTEM SHALL <response>`,
  `WHILE <state> THE SYSTEM SHALL <response>`, `IF <condition> THEN THE SYSTEM SHALL <response>`,
  and `THE SYSTEM SHALL <response>` for always-true behavior.
- "The system" is the `card_identifier` package and its command line. A requirement names the
  module or command only when the name is part of the contract.

## Changing a spec

- Add a requirement with the next free number in its block.
- Change a requirement's meaning by withdrawing it and adding a new one. A wording fix keeps
  the number.
- Update `rtm.md` in the same pull request. Mark a requirement `Done` only when the code
  exists, and `Verified` only when a tagged test passes.
- Each spec ends with **Current state and gaps**. Keep it true: it lists what exists now and
  which issue closes each gap.

## Status words

`Planned`, `In progress`, `Done` and `Verified` in `rtm.md`. `Withdrawn` for removed
requirements. Issue status is GitHub's: open or closed.

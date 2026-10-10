# Spec: cross-cutting requirements

Non-functional requirements that apply to every component. Numbers 1 to 99.

**NFR-1.** THE SYSTEM SHALL support Python 3.13 and 3.14, and CI SHALL run the test suite on
both.
*Check:* the CI matrix lists both versions and passes.

**NFR-2.** THE SYSTEM SHALL record the code version, the config hash, the seed and the hashes
of input files in every catalog, build, run, index, bundle and report it writes.
*Check:* a test per artifact type finds the fields.

**NFR-3.** THE SYSTEM SHALL NOT persist data with pickle, and SHALL NOT load a pickle file,
except in the one-time reader that migrates an old data root (FR-105).
*Check:* `grep -rn "import pickle" card_identifier` finds only the migration reader. The
random-state commands no longer use pickle.

**NFR-4.** THE SYSTEM SHALL set a timeout and a bounded retry count on every outbound HTTP
request.
*Check:* a test lists HTTP call sites and finds none without both.

**NFR-5.** THE SYSTEM SHALL test the transform chain, the serializers and the file layout
without stubbing them. A test MAY fake the network, the process pool and the clock.
*Check:* the suite holds an end-to-end test that builds images with the real chain. CI reports
line coverage of `card_identifier`, and the threshold is set after the first measurement.

**NFR-6.** WHEN a build or training command finishes, THE SYSTEM SHALL print its duration and
its throughput (images per second).
*Check:* the final log lines of `build` include both numbers.

**NFR-7.** THE SYSTEM SHALL validate downloaded images before use and set a maximum pixel
count for decoding. It SHALL build file names from card ids with `file_name(id)`, which
percent-encodes every character outside `A-Za-z0-9._-`, refuses an empty id or one that starts
with `.`, and fails when two ids give names that are equal after lowercasing.
*Check:* a decompression-bomb fixture is rejected. `exu-!` and `exu-%3F` get different names,
`a/b` becomes `a%2Fb`, `../x` is refused, and `A1` with `a1` fails.

**NFR-8.** THE SYSTEM SHALL record the licence of every pretrained weight it uses, SHALL keep
card images out of git and out of container images, and SHALL document where backgrounds
come from.
*Check:* `.gitignore` and `.dockerignore` cover `data/`. The README has a licensing section.

**NFR-9.** THE SYSTEM SHALL let a new game be added by a games package and one registry
entry, with no edit to core modules.
*Check:* the stub-game test in FR-115.

**NFR-10.** THE SYSTEM SHALL run every command without a graphical display.
*Check:* the CI job has no display and passes.

**NFR-11.** THE SYSTEM SHALL list every requirement in `docs/rtm.md`, and a script SHALL fail
when a requirement is missing from it or a test tag names an unknown requirement.
*Check:* the script runs in the pre-commit hooks.

**NFR-12.** THE SYSTEM SHALL pass its debug setting to worker processes, because `spawn`
workers do not inherit logging configuration.
*Check:* a test asserts that `DatasetBuilder.run` sets `CARDIDENT_DEBUG` from the active log level, and
that `gen_random_dataset` reads it.

## Current state and gaps

- NFR-1 holds: CI runs 3.13 and 3.14.
- NFR-12 holds in code (`DatasetBuilder.run` copies the flag into `CARDIDENT_DEBUG`,
  `generator.py:149`) and has no test.
- NFR-5 fails today: tests stub `random_perspective_transform` in three places, assign to the
  global `config` without `monkeypatch`, and no coverage tool is installed
  (#84).
- NFR-11 has no script yet (#99).
- NFR-3, NFR-4, NFR-7 and NFR-8 are met by the catalog and generator issues
  (#88, #82, #98).
- NFR-10 holds: every command is headless and CI has no display.
- NFR-2, NFR-6 and NFR-9 are met by the issues in the table below.

| Requirement | Closed by |
|---|---|
| NFR-3 | #88, #79, #86 |
| NFR-4, NFR-7 | #82 |
| NFR-5, NFR-12 | #84 |
| NFR-8 | #98 |
| NFR-9 | #92 |
| NFR-11 | #99 |
| NFR-2 | #90, #102, #103, #106, #108 |
| NFR-6 | #90, #102 |

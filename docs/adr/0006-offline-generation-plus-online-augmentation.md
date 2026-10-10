# ADR-0006: Keep offline generation, and add light online augmentation

## Status
Proposed (2026-10-09)

## Context
The generator writes every variant to disk as a PNG with a sidecar. The files give provenance,
a stable dataset to inspect and share between builds, and reproducible training. They cost
disk and generation time: 20,000 cards at 100 variants is 2 million files.

Modern training pipelines also augment on the fly, with a new random draw each epoch. That
widens variety at no disk cost, but leaves no record of what the model saw.

## Decision (proposed)
Keep offline generation for the geometry and scene the project cares about: perspective,
rotation, background, placement, glare and occlusion. These are recorded in sidecars and the
manifest. Add online augmentation in the training loader for cheap photometric changes only
(color jitter, small blur, random crop), seeded and recorded in the run config
([FR-409](../specs/training.md)).

### Alternatives considered
- **Offline only.** Simplest. Variety is limited by the number of stored variants.
- **Online only.** Smallest disk use. Loses sidecars, and the transform chain would move into
  the training code.

## Consequences
- Disk use stays the main cost of a large build, so the manifest lets builds share files
  ([FR-307](../specs/selection.md)).
- Two places apply augmentation. The run config says which online settings were used.
- The decision is reversible: turn `augment.online` off.

## References
- [generation.md](../specs/generation.md), [training.md](../specs/training.md)

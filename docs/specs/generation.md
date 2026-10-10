# Spec: dataset generation

The generator turns one reference scan into many randomized training images that look like
camera photos, and records every transform it applied.

Intent: outcome 2 (believable synthetic photos) in [intent.md](../intent.md). Decision:
[ADR 0006](../adr/0006-offline-generation-plus-online-augmentation.md).

## Transform chain

Today the chain is, in order: an optional color or noise transform, a random resize, a random
perspective, a random rotation, then a paste onto a solid color or a stretched background
image. The result is resized to 224x224 and saved as PNG. The target chain keeps this shape and
adds scale normalization first, realism transforms (glare, blur, lighting, JPEG, occlusion)
and aspect-preserving backgrounds. Each step reads its ranges from the generator config.

## Sidecar

Each image `<hash>.png` has a sidecar `<hash>.json`:

```json
{
  "schema_version": 1,
  "filename": "<hash>.png",
  "card_id": "swsh3-136",
  "seed": 123456789,
  "steps": [
    {"name": "scale", "params": {"reference_height": 1000, "factor": 1.04}},
    {"name": "perspective", "params": {"corners": [[0, 0], [1, 0], [1, 1], [0, 1]]}},
    {"name": "rotate", "params": {"degrees": 213}}
  ],
  "background": {"kind": "image", "file": "desk-03.jpg"},
  "placement": {"x": 120, "y": 88}
}
```

`steps` is an ordered list, so two steps of the same kind never overwrite each other. Every
value is a JSON-native type (string, number, bool, list, object, null).

## Requirements

**FR-201.** WHEN the generator saves an image, THE SYSTEM SHALL write a sidecar that parses
with the standard `json` module, and SHALL write the sidecar and the image so that neither
exists without the other after a crash.
*Check:* a test runs the real transform chain with no stubs and parses every sidecar. A
simulated crash between writes leaves no orphan.

**FR-202.** THE SYSTEM SHALL record the transform steps in an ordered `steps` list, with each
step's name and parameters, and SHALL NOT merge steps into one flat object.
*Check:* an image made with resize, perspective and rotate shows three entries in order.

**FR-203.** THE SYSTEM SHALL write only JSON-native values to a sidecar, converting NumPy
scalars and arrays before writing.
*Check:* the sidecar test above covers the perspective step, which holds a NumPy array today.

**FR-204.** THE SYSTEM SHALL derive each image's random seed from the build seed, the card id
and the image index, and SHALL produce byte-identical images for equal inputs regardless of
the number of worker processes.
*Check:* two builds of 20 cards, one with 1 worker and one with 4, give equal image hashes.

**FR-205.** THE SYSTEM SHALL draw all randomness in transforms, backgrounds and placement from
the per-image seeded generator, and SHALL NOT use the global `random` module or an unseeded
library generator.
*Check:* a test replaces the global `random` module with an object that raises on use, and a
build still passes. The noise step takes the same generator.

**FR-206.** THE SYSTEM SHALL read transform probabilities and ranges from a TOML generator
config, SHALL ship a default config that reproduces the documented defaults, and SHALL record
the config in the build manifest.
*Check:* changing `rotate.max_degrees` in a config changes the rotations in a build.

**FR-207.** WHEN the config enables color or noise transforms, THE SYSTEM SHALL apply them
with the configured probability.
*Check:* with probability 1.0 every sidecar lists one such step. With 0.0 none does.

**FR-208.** THE SYSTEM SHALL size the working canvas to contain the whole transformed card,
and SHALL crop the card at the frame edge only as far as the configured
`max_offframe_fraction` allows.
*Check:* over 2,000 seeded draws, no corner leaves the canvas during perspective, and the card
area visible after placement is at least `1 - max_offframe_fraction`.

**FR-209.** THE SYSTEM SHALL scale every reference scan to a configured reference height
before other transforms, so output card size does not depend on the source scan's resolution.
*Check:* scans of 654x914 and 734x1024 pixels give card heights within one pixel for the same
seed and scale draw.

**FR-210.** THE SYSTEM SHALL ignore files in the backgrounds directory that Pillow cannot open,
SHALL crop backgrounds to the output aspect ratio instead of stretching them, and SHALL fail
before any worker starts when a build needs backgrounds and finds none.
*Check:* a directory holding a `.DS_Store` file and one JPEG works. An empty directory stops
the command with a clear error before the pool starts.

**FR-211.** IF generation for one card fails, THEN THE SYSTEM SHALL record the card id and the
error, continue with the other cards, print generated, skipped and failed counts, and exit 1
when any card failed.
*Check:* a build over three cards where one reference scan is corrupt generates two and exits
1 with a summary naming the third.

**FR-212.** THE SYSTEM SHALL count a variant toward a card's quota only when its image and
sidecar both exist and the sidecar parses, and SHALL report orphans.
*Check:* a directory with one complete variant and one image without a sidecar counts one and
reports one orphan.

**FR-213.** THE SYSTEM SHALL produce images at a configured square size and format, defaulting
to 224 pixels and PNG.
*Check:* a config with `size = 256` yields 256x256 images, recorded in the manifest.

**FR-214.** THE SYSTEM SHALL provide optional realism transforms for glare, blur, lighting
gradient, JPEG compression, sleeve reflection and partial occlusion, each controlled by the
config and each recorded as a step.
*Check:* each transform, enabled alone at probability 1.0, changes the image and adds its
step.

**FR-215.** WHEN `trim-dataset` removes images, THE SYSTEM SHALL remove each image's sidecar
with it, SHALL choose images to keep deterministically from the seed after sorting by name, and
SHALL update any dataset map or manifest that lists them.
*Check:* trimming 5 variants to 2 leaves 2 images, 2 sidecars and no sidecar without an image.
Two runs with one seed keep the same files.

## Current state and gaps

What exists, in `dataset/generator.py`, `image/transformers.py` and `image/background.py`:

- `gen_random_dataset` runs the chain and writes `<sha256>.png` and `<sha256>.json`. It fails
  on every image: the perspective step stores a NumPy array and `json.dump` raises after the
  PNG is saved, leaving a truncated sidecar. Re-runs count PNGs only, so each leaves another
  orphan (#75).
- Sidecar steps overwrite each other's `transformer` and `method` keys
  (#95).
- Workers start with fresh OS entropy, so the saved RNG state does nothing in `spawn` workers.
  Noise uses its own generator (#79).
- One bad file in the backgrounds directory raises `UnidentifiedImageError`. The failing
  worker chunk stops, the other chunks finish, and the command exits 1 with a traceback and no
  summary (#80).
- Ranges are constants. The color and noise branch never runs, because the builder passes
  `xform=False` (#94).
- The perspective canvas is 1.2x while corners can reach 1.4x. In a 2,000-draw simulation,
  1,289 transforms clipped a corner (#96).
- `trim-dataset` deletes images and leaves sidecars (#97).
- No realism transforms beyond noise, posterize, solarize and autocontrast
  (#109).

| Requirement | Closed by |
|---|---|
| FR-201, FR-203, FR-212 | #75 |
| FR-202 | #95 |
| FR-204, FR-205 | #79 |
| FR-206, FR-207, FR-213 | #94 |
| FR-208, FR-209 | #96 |
| FR-210, FR-211 | #80 |
| FR-214 | #109 |
| FR-215 | #97 |

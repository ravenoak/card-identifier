# Spec: evaluation

Evaluation measures a model and its reference index on photographs of physical cards. It
decides which architecture is better, and whether the system is good enough for the robot.

Intent: outcome 5 (honest numbers) in [intent.md](../intent.md).

## Real-photo set

A directory outside git:

```
eval/<set-name>/
  photos/            JPEG or PNG files
  labels.csv         photo,card_id,lighting,background,sleeved,notes
```

`card_id` is a canonical card id. The other columns are free tags used for breakdowns.
The collection protocol (to be written with the first set): one card per photo, the card fills
most of the frame, and photos cover at least three lighting conditions, plain and patterned
backgrounds, and sleeved and unsleeved cards. The set includes some cards that are not in the
index, to measure rejection.

## Requirements

**FR-501.** THE SYSTEM SHALL read a real-photo set from `labels.csv` and a photos directory,
SHALL reject a row whose photo is missing or whose `card_id` is not in the catalog, and SHALL
report the SHA-256 of the labels file.
*Check:* a fixture with one missing photo and one unknown id reports both and evaluates the
rest.

**FR-502.** THE SYSTEM SHALL provide `evaluate`, which runs a model and index on a photo set
and reports top-1 and top-5 accuracy for card id, and accuracy for set, name, rarity,
category and regulation mark taken from the matched card's catalog record.
*Check:* on a fixture where the answers are known, each metric equals a hand-computed value.

**FR-503.** THE SYSTEM SHALL write a report as JSON and Markdown with the metrics, a
per-set breakdown, a breakdown per tag column, the most confused card pairs, the list of
failed photos, and the hashes of the model, the index, the manifest and the photo labels.
*Check:* the report for the fixture holds every listed section.

**FR-504.** THE SYSTEM SHALL provide `compare`, which tabulates several reports side by side
and SHALL refuse reports that used different photo-label hashes.
*Check:* two fixture reports on one set compare. A report on another set is refused.

**FR-505.** THE SYSTEM SHALL label every metric computed on synthetic validation images as
synthetic and SHALL NOT place it in the headline table.
*Check:* the Markdown report separates "Real photos" from "Synthetic validation".

**FR-506.** WHEN a photo's best match scores below a threshold, THE SYSTEM SHALL return
"unknown", SHALL report the unknown rate for in-index and out-of-index photos, and SHALL
report how the threshold was chosen.
*Check:* on a fixture with 2 out-of-index photos, the report counts them as correctly rejected
or wrongly accepted.

**FR-507.** THE SYSTEM SHALL report model size on disk and median per-image latency on the
device used.
*Check:* the report holds both numbers with the device name.

## Current state and gaps

Nothing exists. The notebooks plot synthetic validation accuracy only, and `xfer_model.ipynb`
plots `range(500)` for a 10-epoch run.

| Requirement | Closed by |
|---|---|
| FR-501, FR-502, FR-503, FR-505, FR-506, FR-507 | #106 |
| FR-504 | #107 |

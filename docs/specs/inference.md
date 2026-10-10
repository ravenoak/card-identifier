# Spec: inference and export

Inference turns a photo into a card id and its labels. Export packages a trained model and its
index so a consumer, such as the sorting robot, runs it without this project's training code.

Intent: outcome 6 (a usable identifier) in [intent.md](../intent.md).

## Identify result

```json
{
  "photo": "frame-0042.jpg",
  "matches": [
    {"card_id": "swsh3-136", "score": 0.91,
     "labels": {"name": "Furret", "set_id": "swsh3", "rarity": "Uncommon",
                "category": "Pokemon", "types": ["Colorless"],
                "regulation_mark": "D", "legal_standard": false, "legal_expanded": true}}
  ],
  "unknown": false
}
```

`matches` holds the top-k, best first.

## Requirements

**FR-601.** THE SYSTEM SHALL provide `identify`, which takes one or more photo paths, a run or
bundle, and `--top-k`, and prints one result object per photo as JSON lines.
*Check:* a test identifies two fixture photos and parses two lines.

**FR-602.** THE SYSTEM SHALL use one preprocessing function, taking its parameters from the
backbone registry entry, for training, indexing, evaluation and inference.
*Check:* a test calls the function from each of the four paths and compares tensors for one
image.

**FR-603.** THE SYSTEM SHALL export the embedding model to ONNX with the preprocessing
parameters stored in the file's metadata, with `export-bundle`, and SHALL verify that the
L2-normalized ONNX and PyTorch embeddings of 20 sample images differ by less than 1e-4 in
every component.
*Check:* `export-bundle` fails when the difference exceeds 1e-4, and the measured maximum is
in the model card.

**FR-604.** THE SYSTEM SHALL write a self-contained bundle directory with `model.onnx`, the
index vectors, the index ids, the card label records of indexed cards, and `model-card.json`,
and `identify` SHALL run from the bundle alone.
*Check:* `identify` runs in an environment without `torch`, from a bundle copied to an
empty directory with no data root.

**FR-605.** WHEN `identify` reads a photo, THE SYSTEM SHALL apply EXIF orientation, convert to
RGB, and report a clear error for a file that is not an image, without stopping on the other
photos.
*Check:* a PNG with alpha, a rotated JPEG and a text file give two results and one error.

## Current state and gaps

`scripts/label_image.py` is a copy of the TensorFlow Lite sample. Its defaults normalize input
to [-1, 1] with mean and standard deviation 127.5, where TF Hub models expect [0, 1]. It passes
the image through without dropping an alpha channel, and the project's own images are RGBA at
load time. It is excluded from type checking, and its only test runs `--help` and is skipped
when TensorFlow is missing. It is replaced
by `identify`.

| Requirement | Closed by |
|---|---|
| FR-601, FR-603, FR-604, FR-605 | #108 |
| FR-602 | #100, #108 |

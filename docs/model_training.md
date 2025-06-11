# Model Training

This guide explains how to train image classifiers using the provided
`run_mkimgclsfr.sh` script and the Dockerfiles found under `deploy/`.

## `scripts/run_mkimgclsfr.sh`

The script is a thin wrapper around the TensorFlow Hub `make_image_classifier`
command. Run it with the card type and dataset namespace you wish to train on:

```bash
./scripts/run_mkimgclsfr.sh pokemon base_set
```

The command expects your training images to live in
`$IMAGEDIR/<card_type>/<namespace>` (by default `data/images/dataset`).  It
produces a TensorFlow SavedModel, a TFLite model and a label map.  Outputs are
written to directories beneath `$APP_ROOT` which defaults to `/app`.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ROOT` | `/app` | Root directory for datasets and models inside the container. |
| `DATASET_DIR_BASE` | `data/images/dataset` | Location of dataset images relative to `APP_ROOT`. |
| `IMAGEDIR` | `$APP_ROOT/$DATASET_DIR_BASE` | Directory containing training images. |
| `TFHUB_MODULE` | `https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/feature_vector/2` | TensorFlow Hub module to use as the feature extractor. |
| `TRAINING_IMAGE_SIZE` | `224` | Input image size for the model. |
| `MODEL_DIR` | `$APP_ROOT/models/tf2` | Destination directory for the SavedModel. |
| `LABEL_FILE_DIR` | `$APP_ROOT/models` | Folder where the label map is written. |
| `TFLITE_MODEL_FILE_DIR` | `$APP_ROOT/models/tflite` | Folder for the exported TFLite model. |
| `SUMMARY_DIR` | `$APP_ROOT/logs/tf_summaries` | TensorBoard summary output directory. |
| `TRAINING_EPOCHS` | `10` | Number of training epochs. |

### Outputs

Running the script generates the following artifacts inside `APP_ROOT`:

- `models/tf2/<card_type>/<namespace>/` – TensorFlow SavedModel
- `models/<card_type>.<namespace>.class_labels.txt` – label map
- `models/tflite/<card_type>.<namespace>.tflite` – TFLite model
- `logs/tf_summaries/<card_type>/<namespace>/` – TensorBoard summaries

## Dockerfiles under `deploy/`

Two Dockerfiles are provided to simplify building environments for dataset
creation and model training.

### `deploy/dataset_generator/Dockerfile`

Builds a minimal image containing the `mkdataset` CLI.  The build accepts the
following build arguments:

- `PACKAGE_NAME` – Python package name to install (default
  `collectable_card_identifier`)
- `PACKAGE_VER` – Version string to install (default `0.1.0`)
- `PYTHON_VERSION` – Base Python version (default `3.10`)
- `USER_ID` – UID for the runtime user (default `1000`)
- `USER_NAME` – Name for the runtime user (default `card-identifier`)

After building, run the container with your data directory mounted and invoke
`mkdataset` commands as needed.

### `deploy/model_generator/Dockerfile`

Creates an image with TensorFlow Hub and Jupyter installed for training models.
Build arguments `USER_ID` and `USER_NAME` control the UID and user name inside
the container.  Ports `6006` and `8888` are exposed for TensorBoard and
Jupyter Notebook. Use this image together with `run_mkimgclsfr.sh` to train
classifiers.


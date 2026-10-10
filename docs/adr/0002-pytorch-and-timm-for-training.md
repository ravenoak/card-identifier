# ADR-0002: Train with PyTorch and timm

## Status
Accepted (2026-10-09)

## Context
The project trained with TensorFlow Hub's `make_image_classifier` script
(`scripts/run_mkimgclsfr.sh:35`). That tool was removed in tensorflow-hub 0.14.0 (release notes,
2023-07-13: "Remove make_image_classifier and make_nearest_neighbour_index"). The model
container installs the latest `tensorflow-hub` on a TensorFlow 2.13 base image
(`deploy/model_generator/Dockerfile:4,14`). tensorflow-hub 0.16.1 needs `tf-keras>=2.14.1`.

The package requires Python 3.13 or newer, and CI runs 3.13 and 3.14 (`pyproject.toml:9`,
`.github/workflows/ci.yml:22`). On 2026-10-09 PyPI listed TensorFlow 2.21.0 (2026-03-06) with
wheels for Python 3.10 to 3.13 and none for 3.14. PyTorch 2.14.1 (2026-09-30) has wheels for
3.10 to 3.14. timm 1.0.30 (2026-09-22) provides the pretrained image backbones.

The owner wants several architectures trainable and comparable.

## Decision
Use PyTorch for training and timm for backbones. Keep the backbone choice in a registry
([FR-402](../specs/training.md)). Export to ONNX for consumers ([FR-603](../specs/inference.md)).
Retire the TensorFlow Hub script and the model container (#78). The notebooks that depend on
them are fixed or removed under #110.

### Alternatives considered
- **Keras 3 on TensorFlow.** Keeps the TFLite path. Rejected: it caps the trainer at Python
  3.13, and the project would carry a second Python version for training.
- **Keras 3 on the PyTorch or JAX backend.** Rejected as an extra layer over a library that
  timm already serves directly.

## Consequences
- Training works on Python 3.13 and 3.14, on CUDA, Apple silicon (MPS) and CPU.
- The TFLite sample and `label_image.py` go away. Edge deployment uses ONNX runtimes.
- Pretrained weights come from many sources with different licences, so the registry records
  each ([FR-403](../specs/training.md)). On 2026-10-09 the timm `convnextv2_tiny.fcmae_ft_in22k_in1k`
  weights listed CC-BY-NC-4.0, while `mobilenetv4_conv_medium`, `tf_efficientnetv2_s.in21k_ft_in1k`
  and `google/siglip2-base-patch16-224` listed Apache-2.0.
- PyTorch is a large dependency. It goes in an optional dependency group, so dataset work does
  not install it.

## References
- Training spec: [training.md](../specs/training.md)
- Issue to retire the old path: #78

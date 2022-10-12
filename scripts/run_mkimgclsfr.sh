#!/usr/bin/env bash
set -e

APP_ROOT=${APP_ROOT:-/app}
DATASET_DIR_BASE=${DATASET_DIR_BASE:-data/images/dataset}

IMAGE_DIR=${IMAGEDIR:-"${APP_ROOT}/${DATASET_DIR_BASE}"}
TFHUB_MODULE=${TFHUB_MODULE:-"https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/feature_vector/2"}
TRAINING_IMAGE_SIZE=${TRAINING_IMAGE_SIZE:-224}
TF2_MODEL_DIR=${MODEL_DIR:-"${APP_ROOT}/models/tf2"}
LABEL_FILE_DIR=${LABEL_FILE_DIR:-"${APP_ROOT}/models"}
TFLITE_MODEL_FILE_DIR=${TFLITE_MODEL_FILE_DIR:-"${APP_ROOT}/models/tflite"}
SUMMARY_DIR=${SUMMARY_DIR:-"${APP_ROOT}/logs/tf_summaries"}
TRAINING_EPOCHS=${TRAINING_EPOCHS:-10}

if [ -z "${1}" ] || [ -z "${2}" ]; then
  echo "Usage: ${0} <card_type> <namespace>"
  exit 1
fi
case $1 in
"pokemon")
  CARD_TYPE=${1}
  ;;
*)
  echo "Invalid card type: ${1}"
  exit 1
  ;;
esac


function run() {
  LABEL_FILE="${LABEL_FILE_DIR}/${CARD_TYPE}.${2}.class_labels.txt"
  TFLITE_MODEL_FILE="${TFLITE_MODEL_FILE_DIR}/${CARD_TYPE}.${2}.tflite"

  make_image_classifier --image_dir "${IMAGE_DIR}/${CARD_TYPE}/${2}" \
                        --tfhub_module "${TFHUB_MODULE}" \
                        --image_size "${TRAINING_IMAGE_SIZE}" \
                        --saved_model_dir "${TF2_MODEL_DIR}/${CARD_TYPE}/${2}" \
                        --labels_output_file "${LABEL_FILE}" \
                        --tflite_output_file "${TFLITE_MODEL_FILE}" \
                        --summaries_dir "${SUMMARY_DIR}/${CARD_TYPE}/${2}" \
                        --train_epochs "${TRAINING_EPOCHS}"
}

run "${1}" "${2}"

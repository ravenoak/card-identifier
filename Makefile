IMAGE_DIR_BASE=
DATASET_DIR_BASE=data/images/dataset
TFHUB_MODULE=https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet1k_b0/feature_vector/2
TRAINING_IMAGE_SIZE=224
SAVE_MODEL_BASE=models
SUMMARIES_DIR_BASE=logs/tf_summaries
CONTAINER_DATASET=card-identifier-dataset
CONTAINER_DATASET_CONTEXT=.
CONTAINER_DATASET_FILE=./deploy/dataset_generator/Dockerfile
CONTAINER_MODEL=card-identifier-model
CONTAINER_MODEL_CONTEXT=.
CONTAINER_MODEL_FILE=./deploy/model_generator/Dockerfile
APP_ROOT=/app
SCRIPTS_DIR=${APP_ROOT}/scripts

dataset-container:
	docker build -t "${CONTAINER_DATASET}:latest" -f ${CONTAINER_DATASET_FILE} ${CONTAINER_DATASET_CONTEXT}

model-container:
	docker build -t "${CONTAINER_MODEL}:latest" -f ${CONTAINER_MODEL_FILE} ${CONTAINER_MODEL_CONTEXT}

make_image_classifier:
	docker run --rm -v $(pwd):${APP_ROOT} -w ${APP_ROOT} -u "$(id -u):$(id -g)" ${CONTAINER_MODEL}:latest /app/scripts/run_mkimgclsfr.sh

pokemon_sets:
	poetry run python scripts/pokemon_sets.py | sort > /tmp/pokemon_sets.txt

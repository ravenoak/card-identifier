

dataset-container:
	docker build -t 'card-identifier-dataset:latest' -f ./deploy/dataset_generator/Dockerfile .

model-container:
	docker build -t 'card-identifier-model:latest' -f ./deploy/model_generator/Dockerfile .

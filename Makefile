.DEFAULT_GOAL := help

# Shell to use with Make
SHELL ?= /bin/bash

DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

include $(DIR).env
export

GOOGLE_APPLICATION_CREDENTIALS  ?= $$HOME/gcp.json
GOOGLE_CLOUD_PROJECT            ?= openpandemic-analytics

DATASET    ?= openpandemic_test
TABLE      ?= data_test_es_v1

DATA_DIR         ?= $(DIR)data
DOCKER_DATA_DIR  ?= /tmp/pandemic/data

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: clean-all
clean-all: gcloud-bastion-destroy ## remove all generated resources

.PHONY: gcloud-bastion-destroy
gcloud-bastion-destroy: ## Remove docker container
	@docker rm -f gcloud-bastion > /dev/null 2>&1 || true

.PHONY: gcloud-bastion
gcloud-bastion: ## Run a gcloud docker container to be used as proxy command.

	@docker run -it -d --name gcloud-bastion -w /root \
	   -v $(GOOGLE_APPLICATION_CREDENTIALS):/tmp/gcp.json:ro \
	   -v $(DATA_DIR):$(DOCKER_DATA_DIR) \
	   google/cloud-sdk:alpine sh

	@docker exec gcloud-bastion \
	   sh -c "gcloud auth activate-service-account --key-file=/tmp/gcp.json \
	          && gcloud config set project $(GOOGLE_CLOUD_PROJECT) \
	          && gcloud auth configure-docker -q"

.PHONY: bq-shell
bq-shell: ## Run bq shell
	@docker exec -it gcloud-bastion \
	   sh -c 'bq shell'

.PHONY: bq-create-dataset
bq-create-dataset: ## Create a dataset
	@docker exec gcloud-bastion \
	   sh -c "bq --project_id $(GOOGLE_CLOUD_PROJECT) mk -d --data_location=US $(DATASET)"

.PHONY: bq-create-table
bq-create-table: ## Create a table into a dataset
	@docker exec gcloud-bastion \
	   sh -c "bq mk $(DATASET).$(TABLE)"

.PHONY: bq-upload-data
bq-upload-data: ## Upload data into a existing table
	@docker exec gcloud-bastion \
	   sh -c "bq load --source_format=NEWLINE_DELIMITED_JSON $(DATASET).$(TABLE) $(DOCKER_DATA_DIR)/ES/fake_data_es_v1.json $(DOCKER_DATA_DIR)/bq_data_schema_v1.json \
			  && bq show $(DATASET).$(TABLE)"

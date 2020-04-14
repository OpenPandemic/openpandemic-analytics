#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os

from openpandemic import logger

from google.cloud import bigquery as bq
from google.cloud.bigquery.job import LoadJobConfig


def create_dataset(client: bq.Client, dataset_id: str, location: str) -> bq.Dataset:

    _dataset = bq.Dataset(dataset_id)
    _dataset.location = location

    client.create_dataset(_dataset, exists_ok=True, timeout=30)
    logger.info("Created dataset {}.{}".format(client.project, _dataset.dataset_id))

    return _dataset


def create_table(client: bq.Client, table_id: str, schema_json_file: str, recreate: bool = True):

    schema = client.schema_from_json(schema_json_file)

    try:
        client.get_table(table_id)
        if recreate:
            client.delete_table(table_id)
    except Exception as e:
        logger.info("")
    else:
        logger.info("Table %s was recreated.", table_id)

    _table = bq.Table(table_id, schema=schema)
    client.create_table(_table, exists_ok=True, timeout=30)
    logger.info("Created table: %s", _table.path)

    return _table


def upload_fake_data(client: bq.Client, data_file: str, schema_file: str, table_id: str) -> None:
    job_config = LoadJobConfig(
        schema=client.schema_from_json(schema_file),
        source_format=bq.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    with open(data_file, 'r+b') as f:
        load_job = client.load_table_from_file(f, table_id, job_config=job_config)

    load_job.result()

    try:
        dest_table = client.get_table(table_id)
        logger.info("Loaded %s rows.", dest_table.num_rows)
    except Exception as e:
        logger.error(e)


def get_schema_json_file(client: bq.Client, table_id: str = None, schema_json_file_path: str = None):

    _table = client.get_table(table_id)
    client.schema_to_json(_table.schema, schema_json_file_path)


if __name__ == "__main__":

    # Using default environment variables
    bq_client = bq.Client()

    _dataset_name = "openpandemic_test"
    _table_name = "data_test_es_v1"

    _dataset_id = f'{bq_client.project}.{_dataset_name}'
    _table_id = f'{_dataset_id}.{_table_name}'

    dirname = os.path.dirname(__file__)
    _schema_file = os.path.join(dirname, '../../data/bq_data_schema_v1.json')
    _fake_data_file = os.path.join(dirname, "../../data/ES/fake_data_es_v1.json")

    dataset = create_dataset(bq_client, dataset_id=_dataset_id, location='EU')

    table = create_table(bq_client,
                         table_id=_table_id,
                         schema_json_file=_schema_file)

    upload_fake_data(bq_client,
                     data_file=_fake_data_file,
                     schema_file=_schema_file,
                     table_id=_table_id)

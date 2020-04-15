#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys
import argparse

from openpandemic import logger

from google.cloud import bigquery as bq
from google.cloud.bigquery.job import LoadJobConfig


def create_dataset(client: bq.Client, dataset_id: str, location: str = 'EU'):
    """
    Create dataset, if does't exist by default
    :param client: bq client
    :param dataset_id: canonical dataset id
    :param location: location of the dataset
    :return: None
    """
    dataset = bq.Dataset(dataset_id)
    dataset.location = location

    client.create_dataset(dataset, exists_ok=True, timeout=30)
    logger.info("Created dataset %s.%s", client.project, dataset.dataset_id)


def create_table(client: bq.Client, table_id: str, schema_json_file: str, recreate: bool = False):
    """
    Create a table
    :param client: bq client
    :param table_id: canonical table id
    :param schema_json_file: schema file
    :param recreate: True if table should be created again if exists.
    :return: None
    """
    schema = client.schema_from_json(schema_json_file)

    try:
        client.get_table(table_id)
        if recreate:
            client.delete_table(table_id)
    except Exception as e:
        logger.info("Error finding table: %s. %s", table_id, e)
    else:
        logger.info("Table %s was recreated.", table_id)

    table = bq.Table(table_id, schema=schema)
    client.create_table(table, exists_ok=True, timeout=30)
    logger.info("Created table: %s", table.path)


def load_data(client: bq.Client, data_file: str, schema_file: str, table_id: str) -> None:
    """
    Load data into a table
    :param client: bq client
    :param data_file: data file
    :param schema_file: schema file
    :param table_id: table id
    :return: None
    """
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


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog='openpandemic')

    parser.add_argument('-d', '--dataset', default='openpandemic',
                        help='Dataset name')

    parser.add_argument('-l', '--location', default='US',
                        help='Dataset location')

    parser.add_argument('-t', '--table', default='evaluations',
                        help='Table name')

    parser.add_argument('-sf', '--schema_file', default='data/bq_data_schema_v1.json',
                        help='Table data schema')

    parser.add_argument('-df', '--data_file', required=True,
                        help='Data file.')

    parser.add_argument('-r', '--recreate', default=False,
                        help='Recreate the table if exists')

    args = parser.parse_args(argv)

    bq_client = bq.Client()

    dataset_id = f'{bq_client.project}.{args.dataset}'
    table_id = f'{dataset_id}.{args.table}'

    dirname = os.getcwd()
    schema_file = os.path.join(dirname, args.schema_file)
    data_file = os.path.join(dirname, args.data_file)

    create_dataset(bq_client,
                   dataset_id=dataset_id)

    create_table(bq_client,
                 table_id=table_id,
                 schema_json_file=schema_file,
                 recreate=args.recreate)

    load_data(bq_client,
              data_file=data_file,
              schema_file=schema_file,
              table_id=table_id)


if __name__ == "__main__":

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        logger.warning("... command was interrupted")
        sys.exit(2)
    sys.exit(0)

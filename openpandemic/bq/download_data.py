#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import sys
import argparse

from openpandemic import logger

from google.cloud import bigquery as bq

DATA_SHORT_TYPES = """
SELECT
 country,
 region,
 person_id,
 gender,
 birthmonth_mmyyyy,
 postal_code,
 address_location.postal_code as address_location_postal_code,
 test.id as test_id,
 test.time as test_time,
 test.result as test_result,
 test.location.postal_code as test_location_postal_code
FROM {}
ORDER BY TEST.TIME DESC
"""


def download2csv(client: bq.Client, data_file: str, query: str, sep: str = ',') -> None:
    """
    Download/extract data from BigQuery table
    :param client: BigQuery client
    :param data_file: where data will be written
    :param query: the query
    :param sep: CSV separator character, defaults to ','
    :return:
    """

    # TODO: Expand json/struct data to column values

    df = client.query(query).to_dataframe()

    logger.info('Downloaded %s rows into local dataframe', df.shape[0])

    df.to_csv(data_file, sep=sep, index_label=False, index=False)

    logger.info("CSV file created: %s", data_file)


def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='openpandemic')

    parser.add_argument('-s', '--sep', default=',',
                        help='CSV separator')

    parser.add_argument('-f', '--output_file', default='evaluations.csv',
                        help='File where data will be written.')

    parser.add_argument('-q', '--query', required=True, help='Query')

    args = parser.parse_args(argv)

    bq_client = bq.Client()

    dirname = os.getcwd()
    data_file = os.path.join(dirname, args.output_file)

    download2csv(bq_client,
                 data_file=data_file,
                 query=args.query,
                 sep=args.sep)


if __name__ == "__main__":

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        logger.warning("... command was interrupted")
        sys.exit(2)
    sys.exit(0)

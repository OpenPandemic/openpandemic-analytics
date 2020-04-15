#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
import os
import sys
import argparse
import json

from typing import List

from faker import Faker
import time
import os
from datetime import timezone

from openpandemic import logger

from openpandemic.fake.providers.address.es_ES import Provider as AddressProvider
from openpandemic.fake.providers.covid19 import Provider as Covid19Provider


def run_faker(
        faker: Faker,
        data_path: str,
        nrows: int,
        nrevals: int,
        ndays: int) -> None:
    """
    Run a faker generator to get fake data to openpandemic analytics
    :param faker: Faker instance
    :param data_path: Root directory of data files
    :param nrows: The total number of entries
    :param nrevals: Number of entries which person has mora than one evaluation
    :param ndays: time period in days
    :return: A data file is written on the
    """

    # second per day / evaluations per day, lineal distribution
    precision_seconds = 60 * 60 * 24 / (nrows / ndays)

    time_series = faker.time_series(
        start_date=f'-{ndays}d',
        end_date='now',
        precision=precision_seconds,
        tzinfo=timezone.utc)

    dirname = os.path.dirname(__file__)
    data_file_path = os.path.join(dirname, data_path)

    start_time = time.time()

    logger.info('Generating fake data ...')

    with open(data_file_path, 'w') as data_file:
        logger.info('Writing %s registries into %s file ...', nrows, data_file_path)
        i = 0
        person_ids: List[str] = []
        for t in time_series:
            if i < (nrows - nrevals):
                person_id = faker.md5()
                person_ids.append(person_id)
            else:
                person_id = faker.word(ext_word_list=person_ids)

            location_postcode = faker.location_postcode()
            region = location_postcode.ccaa_iso
            test_id = faker.md5()
            gender = faker.word(ext_word_list=["man", "woman"])
            birth_date = faker.date_of_birth().strftime("%m/%Y")
            postcode = str(location_postcode.postcode)
            province = location_postcode.get_sublocale_value('province')
            country = location_postcode.get_sublocale_value('country')
            location_postcode_repr = f'{postcode},{location_postcode.location},{province},{country}'
            questions, test_result = faker.covid19_questions_result()

            evaluation = {
                "PERSON_ID": person_id,
                "GENDER": gender,
                "BIRTHMONTH_MMYYYY": birth_date,
                "POSTAL_CODE": postcode,
                "REGION": region,
                "COUNTRY": country,
                "ADDRESS_LOCATION": {
                    "POSTAL_CODE": location_postcode_repr
                },
                "TEST": {
                    "ID": test_id,
                    "RESULT": test_result,
                    "TIME": t[0].strftime('%Y-%m-%d %H:%M:%S %Z'),
                    "LOCATION": {
                        "NEIGHBORHOOD": None,
                        "POSTAL_CODE": location_postcode_repr,
                        "POLITICAL": None
                    },
                    "QUESTIONS": questions
                }
            }

            data_file.write(f'{json.dumps(evaluation)}\n')
            i += 1

        logger.info('All data were written in: %.2gs seconds', time.time() - start_time)


def main(argv=sys.argv[1:]):

    parser = argparse.ArgumentParser(prog='openpandemic',
                                     add_help='''Fake data generator for evaluations''')

    parser.add_argument('-l', '--locale', default='es_ES',
                        help='Locale for the fake data generatorDataset name')

    parser.add_argument('-nrows', type=int, default=500, required=True,
                        help='Number of entries')

    parser.add_argument('-nrevals', type=int, default=400, required=True,
                        help='Numbre of user which have more than one evaluation')

    parser.add_argument('-ndays', type=int, default=60, required=True,
                        help='Number of days. The period of time when evaluations happen.')

    parser.add_argument('-df', '--data_file', required=True,
                        help='File where data will be written into.')

    args = parser.parse_args(argv)

    faker = Faker(args.locale)

    faker.add_provider(AddressProvider)
    faker.add_provider(Covid19Provider)

    dirname = os.getcwd()
    data_file = os.path.join(dirname, args.data_file)

    run_faker(
        faker=faker,
        data_path=data_file,
        nrows=args.nrows,
        nrevals=args.nrevals,
        ndays=args.ndays
    )


if __name__ == "__main__":

    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        logger.warning("... command was interrupted")
        sys.exit(2)
    sys.exit(0)

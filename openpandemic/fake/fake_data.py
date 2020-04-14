#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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
        data_path: str = None,
        size: int = 500,
        num_re_eval: int = 100,
        num_days: int = 60) -> None:
    """
    Run a faker generator to get fake data to openpandemic analytics
    :param faker: Faker instance
    :param data_path: Root directory of data files
    :param size: The total number of entries
    :param num_re_eval: Number of entries which person has mora than one evaluation
    :param num_days: time period in days
    :return: A dta file is written on the
    """

    # second per day / evaluations per day, lineal distribution
    precision_seconds = 60 * 60 * 24 / (size / num_days)

    time_series = faker.time_series(
        start_date=f'-{num_days}d',
        end_date='now',
        precision=precision_seconds,
        tzinfo=timezone.utc)

    dirname = os.path.dirname(__file__)
    data_file_path = os.path.join(dirname, data_path)

    start_time = time.time()

    logger.info('Generating fake data ...')

    with open(data_file_path, 'w') as data_file:
        logger.info('Writing %s registries into %s file ...', size, data_file_path)
        i = 0
        person_ids: List[str] = []
        for t in time_series:
            if i < (size - num_re_eval):
                person_id = faker.md5()
                person_ids.append(person_id)
            else:
                person_id = faker.word(ext_word_list=person_ids)

            region = str(faker.random_int(0, 51))
            test_id = faker.md5()
            gender = faker.word(ext_word_list=["man", "woman"])
            birth_date = faker.date_of_birth().strftime("%m/%Y")
            location_postal_code = faker.location_postcode()
            arr_location_postal_code = location_postal_code.split(',')
            postal_code = arr_location_postal_code[0]
            country = arr_location_postal_code[3]

            questions, test_result = faker.covid19_questions_result()

            evaluation = {
                "PERSON_ID": person_id,
                "GENDER": gender,
                "BIRTHMONTH_MMYYYY": birth_date,
                "POSTAL_CODE": postal_code,
                "REGION": region,
                "COUNTRY": country,
                "ADDRESS_LOCATION": {
                    "POSTAL_CODE": location_postal_code
                },
                "TEST": {
                    "ID": test_id,
                    "RESULT": test_result,
                    "TIME": t[0].strftime('%Y-%m-%d %H:%M:%S %Z'),
                    "LOCATION": {
                        "NEIGHBORHOOD": None,
                        "POSTAL_CODE": location_postal_code,
                        "POLITICAL": None
                    },
                    "QUESTIONS": questions
                }
            }

            data_file.write(f'{json.dumps(evaluation)}\n')
            i += 1

        logger.info('All data were written in: %.2gs seconds', time.time() - start_time)


if __name__ == '__main__':

    _faker = Faker('es_ES')

    _faker.add_provider(AddressProvider)
    _faker.add_provider(Covid19Provider)

    run_faker(
        faker=_faker,
        data_path='../../data/ES/fake_data_es_v1.json',
        size=50,
        num_re_eval=23)

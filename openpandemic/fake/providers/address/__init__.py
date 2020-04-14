# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
from typing import List, Any

import pandas as pd

from openpandemic import logger

from faker.providers.address import Provider as AddressProvider


localized = True


class Provider(AddressProvider):
    """Provider for Faker which adds fake address with more specific locations."""

    @staticmethod
    def get_location_info_csv(csv_file_name: str) -> List[str]:
        """
        Get the location info from csv file.
        :param csv_file_name: CSV file name with the advanced or custom location info
        :return: Pandas dataframe
        """

        logger.debug(f'Reading CSV file: {csv_file_name}')
        csv_file = os.path.join(os.path.dirname(__file__), f"../../../../data/{csv_file_name}")

        arr = pd.read_csv(csv_file, ';').to_numpy()

        return arr

    def location_postcode(self) -> Any:
        """
        Get full location qith postcode
        :return: An instance of location postcode
        """
        return None

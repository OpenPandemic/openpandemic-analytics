# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4

from openpandemic.fake.providers.address import Provider as AddressProvider


class Provider(AddressProvider):
    """Provider for Faker which adds more realistic information."""

    location_postal_codes = AddressProvider.get_location_info_csv(
        csv_file_name="ES/postcodes-iso.csv"
    )

    @staticmethod
    def get_locale_name(name: str, sublocale: bool = True) -> str:
        """
        Return the name with locale language, or sub-locale
        :param name: the name, locale and sub-locale forms are separated with character '/': example 'Ourense/Orense'.
        The sub-locale name has priority by default, it placed at the beginning.
        :param sublocale: Set to False to use only the locale language 'es'
        :return: the name with locale language
        """
        locale_names = name.split('/')
        if not sublocale and (len(locale_names) > 1):
            return locale_names[1]
        else:
            return locale_names[0]

    def get_location_postcode(self):

        index = self.random_int(0, len(self.location_postal_codes) -1 )
        return self.location_postal_codes[index]

    def postcode(self):

        _location_postcode = self.get_location_postcode()
        return _location_postcode[2]

    def location_postcode(self):
        """
        Get location
        :return: postal code location postcode,city,province,country
        """

        # Return a location Town, City, Country
        # i.e.  49440,Cañizal,Zamora,España

        _location_postcode = self.get_location_postcode()
        province = self.get_locale_name(_location_postcode[0])
        town = self.get_locale_name(_location_postcode[1])
        postcode = _location_postcode[2]
        return f'{postcode},{town},{province},España'

    def location_neighborhood(self):
        pass

    def location_political(self):
        pass

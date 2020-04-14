# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
from dataclasses import dataclass, field, fields

from openpandemic.fake.providers.address import Provider as AddressProvider


@dataclass(init=True, repr=True, eq=True, order=False, unsafe_hash=False, frozen=True)
class LocationPostCode:
    province: str = field(metadata=dict(sublocale=True))
    location: str
    postcode: str
    lat: str
    lon: str
    ccaa_iso: str
    ccaa_name: str = field(metadata=dict(sublocale=True))
    province_iso: str
    country: str = field(default='España/Spain', init=False, repr=False, metadata=dict(sublocale=True))
    _locale_sep: str = field(default='/', init=False, repr=False)

    def get_sublocale_value(self, field_name: str, sublocale: bool = True) -> str:
        """
        Return the value with sublocale language, or locale.
        :param field_name: the name of the field. Values have locale and sub-locale forms are separated
                          with character '_locale_sep'. For example: 'Ourense/Orense'.
                          The sub-locale name has priority by default, it's placed at the beginning.
        :param sublocale: Whether choose sublocale o locale value, defaults to sublocale.
        :return: the sublocale or locale value of the field name passed as argument.
        """
        sublocale_field_names = tuple(f.name for f in fields(LocationPostCode)
                                      if f.metadata and f.metadata.get('sublocale'))

        if field_name in sublocale_field_names:
            values = getattr(self, field_name).split(self._locale_sep)
            if not sublocale and (len(values) > 1):
                return values[1]
            else:
                return values[0]
        else:
            return getattr(self, field_name)


class Provider(AddressProvider):
    """Provider for Faker which adds more realistic information."""

    location_postal_codes = AddressProvider.get_location_info_csv(
        csv_file_name="ES/postcodes-iso.csv"
    )

    def _get_location_postcode(self):
        index = self.random_int(0, len(self.location_postal_codes) - 1)
        return LocationPostCode(*self.location_postal_codes[index])

    def location_postcode(self, sublocale: bool = None) -> LocationPostCode:
        location_postcode = self._get_location_postcode()
        if sublocale:
            self._get_location_postcode_sublocale(location_postcode, sublocale)
        return location_postcode

    def postcode(self) -> str:
        _location_postcode = self.get_location_postcode()
        return _location_postcode.postcode

    def location_neighborhood(self):
        pass

    def location_political(self):
        pass

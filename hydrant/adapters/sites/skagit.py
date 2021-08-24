from ...models.datetime import parse_datetime


class SkagitAdapter(object):
    """Specialized site adapter for skagit site exports"""
    SITE_SYSTEM = "SKAGIT"

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'Pat Last Name',
            'Pat First Name',
            'Pat DOB',
            'Written by Prov First Name'
        ]

    def __init__(self, parsed_row):
        self.data = parsed_row

    @property
    def identifier(self):
        """If parsed data include MRN, add a site specific identifier"""
        if 'Pat MRN' in self.data:
            ident = {"system": SkagitAdapter.SITE_SYSTEM, "value": self.data['Pat MRN']}
            # FHIR keeps lists of identifiers, return as list
            return [ident]

    @property
    def name(self):
        return {
            "family": self.data['Pat Last Name'],
            "given": [self.data['Pat First Name']]
            }

    @property
    def birthDate(self):
        if not self.data['Pat DOB']:
            return
        return parse_datetime(self.data['Pat DOB']).date().isoformat()

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('name', 'birthDate', 'identifier'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value

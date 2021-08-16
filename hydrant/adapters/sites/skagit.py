from ...models.datetime import parse_datetime


class SkagitAdapter(object):
    """Specialized site adapter for skagit site exports"""
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
    def name(self):
        return {
            "family": self.data['Pat Last Name'],
            "given": [self.data['Pat First Name']]
            }

    @property
    def birthDate(self):
        if not self.data['Pat DOB']:
            return
        return parse_datetime(self.data['Pat DOB'])

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('name', 'birthDate'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value


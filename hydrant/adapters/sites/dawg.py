import json
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient


class DawgPatientAdapter(object):
    """Specialized site adapter for UW DAWG site exports"""
    RESOURCE_CLASS = Patient
    SITE_SYSTEM = "uwDAL_Clarity"

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'PAT_ID',
            'PAT_FIRST_NAME',
            'PAT_LAST_NAME',
            'BIRTH_DATE'
        ]

    def __init__(self, parsed_row):
        self.data = parsed_row

    @property
    def identifier(self):
        """If parsed data include MRN, add a site specific identifier"""
        mrn_field = 'PAT_ID'
        if mrn_field in self.data:
            ident = {"system": DawgPatientAdapter.SITE_SYSTEM, "value": self.data[mrn_field]}
            # FHIR keeps lists of identifiers, return as list
            return [ident]

    @property
    def name(self):
        return {
            "family": self.data['PAT_LAST_NAME'],
            "given": [self.data['PAT_FIRST_NAME']]
            }

    @property
    def birthDate(self):
        if not self.data['BIRTH_DATE']:
            return
        return parse_datetime(self.data['BIRTH_DATE']).date().isoformat()

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('name', 'birthDate', 'identifier'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value

    def unique_key(self):
        """Returns a key value to represent this item as unique

        Defined by adapters wishing to sort out duplicates, used in
        comparison operators.
        """
        return json.dumps([self.name, self.birthDate])

import json
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient


class KentPatientAdapter(object):
    """Specialized site adapter for kent site exports"""
    RESOURCE_CLASS = Patient
    SITE_SYSTEM = "KentPatientAccountNo"

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'Patient Last Name',
            'Patient First Name',
            'Patient DOB',
            'Patient Acct No'
        ]

    def __init__(self, parsed_row):
        self.data = parsed_row

    @property
    def identifier(self):
        """If parsed data include MRN, add a site specific identifier"""
        mrn_field = 'Patient Account No'
        if mrn_field in self.data:
            ident = {"system": KentPatientAdapter.SITE_SYSTEM, "value": self.data[mrn_field]}
            # FHIR keeps lists of identifiers, return as list
            return [ident]

    @property
    def name(self):
        return {
            "family": self.data['Patient Last Name'],
            "given": [self.data['Patient First Name']]
            }

    @property
    def birthDate(self):
        if not self.data['Patient DOB']:
            return
        return parse_datetime(self.data['Patient DOB']).date().isoformat()

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

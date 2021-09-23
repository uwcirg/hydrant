import json
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient


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

    def unique_key(self):
        """Returns a key value to represent this item as unique

        Defined by adapters wishing to sort out duplicates, used in
        comparison operators.
        """
        return json.dumps([self.name, self.birthDate])


class SkagitServiceRequestAdapter(object):
    """Specialized site adapter for skagit site service request exports"""
    SITE_CODING_SYSTEM = "http://hl7.org/fhir/sid/icd-9"

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'Test Code Ordered',
            'Specimen Date',
            'Pat Last Name',
            'Pat First Name',
            'Pat DOB',
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
        return parse_datetime(self.data['Pat DOB']).date().isoformat()

    @property
    def code(self):
        return {'coding': [
            {'system': self.SITE_CODING_SYSTEM,
             'code': self.data['Test Code Ordered']}
        ]}

    @property
    def subject(self):
        # Look up matching patient
        patient = Patient(name=self.name, birthDate=self.birthDate)
        patient.id()  # force round trip lookup
        return {"reference": patient.search_url()}

    @property
    def occurrenceDateTime(self):
        return parse_datetime(self.data['Specimen Date']).isoformat()

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('subject', 'code', 'occurrenceDateTime'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value

    def unique_key(self):
        """Returns a key value to represent this item as unique

        Defined by adapters wishing to sort out duplicates, used in
        comparison operators.
        """
        return json.dumps([self.subject, self.code, self.occurrenceDateTime])

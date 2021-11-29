from collections import OrderedDict
import jmespath
import json
from hydrant.models.datetime import parse_datetime
from hydrant.models.document_reference import (
    CONTROLLED_SUBSTANCE_AGREEMENT_CODE,
    DocumentReference,
)
from hydrant.models.patient import Patient
from hydrant.models.service_request import ServiceRequest


def labcorp_code_lookup(labcorp_code):
    """Sites such as Skagit send all labs to Labcorp - lookup keyed values

    Given flat CSV files, need to map a code from a known lab system to
    a FHIR Service Request.

    Extend with additional codes as needed.  Look up values at top of
    an existing page such as:
    https://www.labcorp.com/tests/733727/pain-management-screening-profile-11-drugs-urine-pmp-11s

    :returns: dict of `text` and `code` for use in ServiceRequest
    """
    results = {'coding': [
        {'system': "https://www.labcorp.com/tests",
         'code': labcorp_code}
    ]}

    if int(labcorp_code) == 733727:
        results['coding'][0]['display'] = '10+Oxycodone+Crt-Scr'
        results['text'] = "Pain Management Screening Profile (11 Drugs), Urine (PMP-11S)"
    elif int(labcorp_code) == 763824:
        results['coding'][0]['display'] = '12+Oxycodone+Crt-Unbund'
        results['text'] = "Pain Management Profile (13 Drugs), Urine (PMP-13)"
    else:
        raise ValueError(f"Unmapped labcorp code {labcorp_code}")
    return results


class SkagitPatientAdapter(object):
    """Specialized site adapter for skagit site exports"""
    RESOURCE_CLASS = Patient
    SITE_SYSTEM = "SKAGIT"

    @classmethod
    def col_headers_to_fhir_paths(cls):
        """Return minimal expected CSV (column headers: json path) in FHIR - extras ignored"""
        return OrderedDict([
            ('Pat Last Name', 'name[0].family'),
            ('Pat First Name', 'name[0].given[0]'),
            ('Pat DOB', 'birthDate'),
            ('Written by Prov First Name', 'generalPractitioner')
        ])

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return cls.col_headers_to_fhir_paths().keys()

    def __init__(self, parsed_row):
        self.data = parsed_row

    def from_resource(self, resource):
        """Generate class data from FHIR resource form (as opposed to parsing)"""
        assert resource['resourceType'] == self.RESOURCE_CLASS.RESOURCE_TYPE
        results = []
        for json_path in self.col_headers_to_fhir_paths().values():
            value = jmespath.search(json_path, resource) or ""
            results.append(value)
        return results

    @property
    def identifier(self):
        """If parsed data include MRN, add a site specific identifier"""
        if 'Pat MRN' in self.data:
            ident = {"system": SkagitPatientAdapter.SITE_SYSTEM, "value": self.data['Pat MRN']}
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


class SkagitControlledSubstanceAgreementAdapter(object):
    """Specialized site adapter for skagit site controlled substance agreement dates"""
    RESOURCE_CLASS = DocumentReference

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'Controlled Substance Agreement Date',
            'Pat Last Name',
            'Pat First Name',
            'Pat DOB',
        ]

    def __init__(self, parsed_row):
        self.data = parsed_row

    @property
    def name(self):
        """Parsed and used to locate `subject` reference"""
        return {
            "family": self.data['Pat Last Name'],
            "given": [self.data['Pat First Name']]
            }

    @property
    def birthDate(self):
        """Parsed and used to locate `subject` reference"""
        if not self.data['Pat DOB']:
            return
        return parse_datetime(self.data['Pat DOB']).date().isoformat()

    @property
    def type(self):
        return {'coding': [CONTROLLED_SUBSTANCE_AGREEMENT_CODE]}

    @property
    def subject(self):
        # Look up matching patient
        patient = Patient(name=self.name, birthDate=self.birthDate)

        # force round trip lookup - can't continue w/o a known patient
        if patient.id() is None:
            raise ValueError(f"Request to add {self.RESOURCE_CLASS} for non existing {patient.search_url()}")
        return {"reference": patient.search_url()}

    @property
    def date(self):
        return parse_datetime(self.data['Controlled Substance Agreement Date']).isoformat()

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('subject', 'type', 'date'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value

    def unique_key(self):
        """Returns a key value to represent this item as unique

        Defined by adapters wishing to sort out duplicates, used in
        comparison operators.
        """
        return json.dumps([self.subject, self.type, self.date])


class SkagitServiceRequestAdapter(object):
    """Specialized site adapter for skagit site service request exports"""
    RESOURCE_CLASS = ServiceRequest

    @classmethod
    def headers(cls):
        """Return minimal expected header values - extras ignored"""
        return [
            'Test Code Ordered',
            'Order Date',
            'Pat Last Name',
            'Pat First Name',
            'Pat DOB',
        ]

    def __init__(self, parsed_row):
        self.data = parsed_row

    @property
    def name(self):
        """Parsed and used to locate `subject` reference"""
        return {
            "family": self.data['Pat Last Name'],
            "given": [self.data['Pat First Name']]
            }

    @property
    def birthDate(self):
        """Parsed and used to locate `subject` reference"""
        if not self.data['Pat DOB']:
            return
        return parse_datetime(self.data['Pat DOB']).date().isoformat()

    @property
    def code(self):
        return labcorp_code_lookup(self.data['Test Code Ordered'])

    @property
    def subject(self):
        # Look up matching patient
        patient = Patient(name=self.name, birthDate=self.birthDate)

        # force round trip lookup - can't continue w/o a known patient
        if patient.id() is None:
            raise ValueError(f"Request to add {self.RESOURCE_CLASS} for non existing {patient.search_url()}")
        return {"reference": patient.search_url()}

    @property
    def authoredOn(self):
        return parse_datetime(self.data['Order Date']).isoformat()

    def items(self):
        """Performs like a dictionary, returns key, value for known/found attributes"""
        for attr in ('subject', 'code', 'authoredOn'):
            value = getattr(self, attr, None)
            if value:
                yield attr, value

    def unique_key(self):
        """Returns a key value to represent this item as unique

        Defined by adapters wishing to sort out duplicates, used in
        comparison operators.
        """
        return json.dumps([self.subject, self.code, self.authoredOn])

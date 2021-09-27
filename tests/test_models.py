from datetime import date, datetime
import json
from urllib.parse import parse_qs, urlparse

from hydrant.models.bundle import Bundle
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient
from hydrant.models.service_request import ServiceRequest


def test_date_parse():
    ex = '1/21/1950'
    result = parse_datetime(ex)
    assert isinstance(result, datetime)
    assert result.date() == date(year=1950, month=1, day=21)


def test_2d_year_wrap():
    ex = '01-01-66'
    result = parse_datetime(ex)
    assert result.year == 1966

    ex2 = '11-28-51'
    result = parse_datetime(ex2)
    assert result.year == 1951

    ex3 = '11-25-01'
    result = parse_datetime(ex3)
    assert result.year == 2001


def test_patient_bundle():
    bundle = Bundle()
    patient = Patient()
    bundle.add_entry(patient.as_fhir())
    assert bundle.as_fhir()['total'] == 1
    # Confirm entire bundle is serializable
    json.dumps(bundle.as_fhir())


def test_service_request():

    # Mock patient as subject
    name = {'family': 'Brown', 'given': ['Charlie']}
    dob = "1948-05-30"
    codeable_concept = {"coding": [{'system': 'http://loinc.org', 'code': 'chicken'}]}

    patient = Patient(name=name, birthDate=dob)
    patient._id = '9'

    # Mock ServiceRequest with code
    svc_req = ServiceRequest()
    svc_req._fields['authoredOn'] = "2021-09-27"
    svc_req._fields['subject'] = {'reference': patient.search_url()}
    svc_req._fields['code'] = codeable_concept

    # as FHIR, includes subject reference and codeable concept
    f = svc_req.as_fhir()
    assert(f['subject'] == {'reference': 'Patient/9'})
    assert(f['code']) == codeable_concept

    # for HAPI search URL - subject points directly to id and code is '|' together
    s = svc_req.search_url()
    parsed = urlparse(s)
    assert(parsed.path == 'ServiceRequest/')
    assert('Patient' in parsed.query)
    qs = parse_qs(parsed.query)
    assert(qs['subject'] == ['Patient/9'])
    assert(qs['code'] == ['http://loinc.org|chicken'])
    assert(qs['authoredOn'] == ['2021-09-27'])

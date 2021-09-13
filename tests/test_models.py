from datetime import date, datetime
import json

from hydrant.models.bundle import Bundle
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient


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

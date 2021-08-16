from datetime import date, datetime

from hydrant.models.bundle import Bundle
from hydrant.models.datetime import parse_datetime
from hydrant.models.patient import Patient


def test_date_parse():
    ex = '1/21/1950'
    result = parse_datetime(ex)
    assert isinstance(result, datetime)
    assert result.date() == date(year=1950, month=1, day=21)


def test_patient_bundle():
    bundle = Bundle()
    patient = Patient()
    bundle.add_entry(patient.as_fhir())
    assert bundle.as_fhir()['total'] == 1

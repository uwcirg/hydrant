from datetime import datetime
import pytest
import os

from hydrant.adapters.csv import CSV_Parser
from hydrant.adapters.sites.skagit import SkagitAdapter
from hydrant.models.patient import PatientList


@pytest.fixture
def parser_skagit1_csv(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'skagit1.csv'))
    return parser


@pytest.fixture
def example_csv(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'example.csv'))
    return parser


@pytest.fixture
def parser_dups_csv(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'dups.csv'))
    return parser


def test_csv_headers(parser_skagit1_csv):
    assert parser_skagit1_csv.headers[:2] == ['Pat Last Name', 'Pat First Name']
    assert not set(SkagitAdapter.headers()).difference(set(parser_skagit1_csv.headers))


def test_csv_patients(parser_skagit1_csv):
    pl = PatientList(parser_skagit1_csv, SkagitAdapter)
    assert len(pl.patients()) == 2
    for pat in pl.patients():
        assert pat.as_fhir()['resourceType'] == 'Patient'
        assert pat.as_fhir()['name']['given'] in (['Barney'], ['Fred'])
        assert isinstance(pat.as_fhir()['birthDate'], str)


def test_example_patients(example_csv):
    pl = PatientList(example_csv, SkagitAdapter)
    assert len(pl.patients()) == 10
    for patient in pl.patients():
        fp = patient.as_fhir()
        assert len(fp['identifier']) == 1


def test_dups_example(parser_dups_csv):
    pl = PatientList(parser_dups_csv, SkagitAdapter)
    assert len(pl.patients()) == 2
    for patient in pl.patients():
        fp = patient.as_fhir()
        assert fp['name']['family'] in ("Potter", "Granger")

import pytest
import os

from hydrant.adapters.csv import CSV_Parser
from hydrant.adapters.sites.kent import KentPatientAdapter
from hydrant.adapters.sites.skagit import SkagitPatientAdapter, SkagitServiceRequestAdapter
from hydrant.models.resource_list import ResourceList


@pytest.fixture
def parser_kent1_csv(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'kent1.csv'))
    return parser


@pytest.fixture
def parser_skagit1_csv(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'skagit1.csv'))
    return parser


@pytest.fixture
def skagit_service_requests(datadir):
    parser = CSV_Parser(os.path.join(datadir, 'skagit_service_requests.csv'))
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
    assert not set(SkagitPatientAdapter.headers()).difference(set(parser_skagit1_csv.headers))


def test_csv_patients(parser_skagit1_csv):
    pl = ResourceList(parser_skagit1_csv, SkagitPatientAdapter)
    assert len(pl) == 2
    for pat in pl:
        assert pat.as_fhir()['resourceType'] == 'Patient'
        assert pat.as_fhir()['name']['given'] in (['Barney'], ['Fred'])
        assert isinstance(pat.as_fhir()['birthDate'], str)


def test_kent_patients(parser_kent1_csv):
    pl = ResourceList(parser_kent1_csv, KentPatientAdapter)
    assert len(pl) == 1
    for pat in pl:
        f = pat.as_fhir()
        assert f['resourceType'] == 'Patient'
        assert f['name']['family'] == 'Aabb'
        assert f['name']['given'] == ['Cccddee']
        assert isinstance(pat.as_fhir()['birthDate'], str)


def test_example_patients(example_csv):
    pl = ResourceList(example_csv, SkagitPatientAdapter)
    assert len(pl) == 10
    for patient in pl:
        fp = patient.as_fhir()
        assert len(fp['identifier']) == 1


def test_dups_example(parser_dups_csv):
    pl = ResourceList(parser_dups_csv, SkagitPatientAdapter)
    assert len(pl) == 2
    for patient in pl:
        fp = patient.as_fhir()
        assert fp['name']['family'] in ("Potter", "Granger")
        assert fp['birthDate'] in ('1966-01-01', '1972-11-25')


def test_skagit_service_requests(skagit_service_requests):
    srl = ResourceList(skagit_service_requests, SkagitServiceRequestAdapter)
    assert len(srl) == 5
    for sr in srl:
        f = sr.as_fhir()
        assert f['code'] == {'coding': [{
            'code': '733727',
            'system': SkagitServiceRequestAdapter.SITE_CODING_SYSTEM}]}

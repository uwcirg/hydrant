import click
from flask import Blueprint, current_app
import requests

from hydrant.models.bundle import Bundle
from hydrant.models.patient import PatientList

base_blueprint = Blueprint('base', __name__, cli_group=None)


@base_blueprint.route('/')
def root():
    return {"message": "ok"}


@base_blueprint.cli.command("upload")
@click.argument("filename")
def upload_file(filename):
    """Parse and upload content in named file

    Seek out given filename from configured upload directory.  Parse
    the file, and push results to configured FHIR store.
    """
    try:
        with open(filename, 'r') as f:
            pass
    except FileNotFoundError:
        raise click.FileError(f"'{filename}'", "File not found")

    # Locate best parser and adapter
    # TODO: move this process to factory methods
    parser, adapter = None, None
    if filename.endswith('csv'):
        from hydrant.adapters.csv import CSV_Parser
        from hydrant.adapters.sites.skagit import SkagitAdapter
        parser = CSV_Parser(filename)
        headers = set(parser.headers)

        # sniff out the site adapter from the header values
        for site_adapter in (SkagitAdapter,):
            if not set(site_adapter.headers()).difference(headers):
                if adapter:
                    raise click.BadParameter("column headers match multiple adapters")
                adapter = site_adapter
        if not adapter:
            raise click.BadParameter("column headers not found in any available adapters")
    else:
        raise click.BadParameter("no appropriate parsers found; can't continue")

    # With parser and adapter at hand, process the data
    bundle = Bundle()
    patients = PatientList(parser, adapter)
    for p in patients.patients():
        bundle.add_entry(p.as_upsert_entry())

    fhir_bundle = bundle.as_fhir()
    click.echo(f"  - parsed {fhir_bundle['total']} patients")

    target_system = current_app.config['FHIR_SERVER_URL']
    click.echo(f"  - uploading bundle to {target_system}")

    response = requests.post(target_system, json=fhir_bundle)
    click.echo(f"  - response status {response.status_code}")

    if response.status_code != 200:
        raise click.BadParameter(response.text)

    click.echo("upload complete")

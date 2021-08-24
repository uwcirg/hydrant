# HYDRANT

Goofy name for a tool to simplify parsing and importing data from disparate sources
destined for a FHIR backend.

Adapters exist or can be added for different data souces (i.e. CSV, MySQL)
and nested `adapters/sites` modules implement specifics to adapt format and attribute details
from the given source to common FHIR Resource types.

Regardless of source, the generated FHIR Bundle prepared is ready for consumption
by the configured FHIR endpoint

## Usage

Example invocation, using a test file for patient upsert:
```bash
flask upload ../tests/test_adapters/example.csv
```

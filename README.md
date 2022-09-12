# HYDRANT

An ETL (Extract, Transform, Load) framework, intended to be
flexible in supporting multiple input formats and data sources, with the
primary goal of transforming legacy health care data formats into FHIR
(Fast Healthcare Interoperability Resources).

Adapters exist or can be added for different data sources (i.e. CSV, MySQL)
and nested `adapters/sites` modules implement specifics to adapt format and
attribute details from the given source to common FHIR Resource types.

Regardless of source, the generated FHIR Bundle prepared is ready for
consumption by the configured FHIR endpoint, and typically fed (PUT/POST)
directly to said endpoint. Generating a bundle artifact would be an easy
adaptation if the need arises.

## FHIR Resource Interdependence

Exporting a single CSV file from a legacy system often includes columns
whose data span multiple FHIR resource types, implicitly or explicitly.
For example, a set of questionnaire responses for a given patient may be
in a single file spanning what maps to several distinct Questionnaires,
QuestionnaireResponses, Encounters and of course the Patient.
The patient in question may be part of the file name, or in one or more
columns with a legacy identifier or data to uniquely identify the resource,
say (first name, last name, date of birth).

At this time, import files must define all necessary related data, i.e.
some form of a patient lookup (first, last, DOB or maybe an external
identifier) for association with the other FHIR Resources being assembled.

Mapping files or multiple CSV files may be needed to define interdependent
resources and associations.  Incomplete work at this time, but it is expected
we'll need to front load the system with say a set of Questionnaires or
provide a mapping resource along with a CSV that lacks details to build
the associations between legacy question identifiers and their respective
`QuestionnaireResponse.item[].linkId` 

## Usage

Example invocation, using a test file for patient upsert:
```bash
flask upload ../tests/test_adapters/example.csv
```

## Supported FHIR Resource Types

- Patient
- ServiceRequest
- Condition (pending)
- Encounter (pending)
- Medication (pending)
- QuestionnaireResponse (pending)


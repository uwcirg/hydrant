from collections import OrderedDict
import requests


class PatientList(object):
    """Like a factory, used to build a list of patients via parser"""
    def __init__(self, parser, adapter):
        self.parser = parser
        self.adapter = adapter
        self.items = None

    def _parse(self):
        """Use parser and adapter, build up list of available patients"""
        self.items = []
        keys_seen = set()
        for row in self.parser.rows():
            # Adapter may define unique_key() - if defined and a previous
            # entry matches, skip over this "duplicate"
            if hasattr(self.adapter, 'unique_key'):
                key = self.adapter(row).unique_key()
                if key in keys_seen:
                    continue
                keys_seen.add(key)

            self.items.append(Patient.factory(row, self.adapter))

    def patients(self):
        if self.items is None:
            self._parse()

        return self.items


class Patient(object):
    """Minimal FHIR like Patient for parsing / uploading """
    def __init__(self):
        self._fields = OrderedDict()

    def __repr__(self):
        if 'id' in self._fields:
            return f"<Patient {self._fields['id']}>"
        elif 'name' in self._fields:
            return f"<Patient {self._fields['name']}"
        else:
            return f"<Patient>"

    def as_fhir(self):
        results = {'resourceType': 'Patient'}
        results.update(self._fields)
        return results

    def as_upsert_entry(self, target_system=None):
        """Generate FHIR for inclusion in transaction bundle

        Transaction bundles need search and method details for
        FHIR server to perform requested task.

        :param target_system: define to perform lookup for existing
        :returns: JSON snippet to include in transaction bundle
        """
        results = {}
        results['resource'] = self.as_fhir()
        method = 'POST'

        # FHIR spec: 'birthDate'; HAPI search: 'birthdate'
        patient_url = (
            f'Patient?family={self._fields["name"]["family"]}&'
            f'given={self._fields["name"]["given"][0]}&'
            f'birthdate={self._fields["birthDate"]}')

        # Round-trip to see if this represents a new or existing Patient
        if target_system:
            response = requests.get(target_system+patient_url)
            response.raise_for_status()

            # extract Patient.id from bundle
            bundle = response.json()
            if bundle['total']:
                if bundle['total'] > 1:
                    raise RuntimeError(
                        "Found multiple matches, can't generate upsert"
                        f"for {patient_url}")
                assert bundle['entry'][0]['resource']['resourceType'] == 'Patient'
                method = 'PUT'
                patient_url = f"Patient/{bundle['entry'][0]['resource']['id']}"

        results['request'] = {
            'method': method,
            'url': patient_url}
        return results

    @classmethod
    def factory(cls, data, adapter_cls):
        """Using parser API, pull available Patient fields

        :param data: single `row` of data, from parsed file or db
        :param adapter_cls: class to be instantiated on `data` with
          accessor methods to obtain patient attributes from given
          format.

        :returns: populated Patient instance, from parsed data
        """

        # Use given adapter to parse "row" data
        adapter = adapter_cls(data)

        # Populate instance with available data from adapter / row
        patient = cls()
        for key, value in adapter.items():
            if not value:
                continue
            patient._fields[key] = value

        return patient

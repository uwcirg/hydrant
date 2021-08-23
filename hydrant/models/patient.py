from collections import OrderedDict


class PatientList(object):
    """Like a factory, used to build a list of patients via parser"""
    def __init__(self, parser, adapter):
        self.parser = parser
        self.adapter = adapter
        self.items = None

    def _parse(self):
        """Use parser and adapter, build up list of available patients"""
        self.items = []
        for row in self.parser.rows():
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

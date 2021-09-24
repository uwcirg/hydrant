from urllib.parse import urlencode

from hydrant.models.resource import Resource


class Patient(Resource):
    """Minimal FHIR like Patient for parsing / uploading """
    RESOURCE_TYPE = 'Patient'

    def __init__(self, name=None, birthDate=None):
        super().__init__()
        if name:
            self._fields['name'] = name
        if birthDate:
            self._fields['birthDate'] = birthDate

    def search_url(self):
        """Generate the request path search url for Patient

        NB - this method does NOT invoke a round trip ID lookup.
        Call self.id() beforehand to force a lookup.
        """
        if self._id:
            return f"{self.RESOURCE_TYPE}/{id}"

        # FHIR spec: 'birthDate'; HAPI search: 'birthdate'
        search_params = {
            "family": self._fields["name"]["family"],
            "given": self._fields["name"]["given"][0],
            "birthdate": self._fields["birthDate"],
        }
        return f"{self.RESOURCE_TYPE}/?{urlencode(search_params)}"

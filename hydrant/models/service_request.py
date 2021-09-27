from urllib.parse import urlencode

from hydrant.models.resource import Resource


class ServiceRequest(Resource):
    """Minimal FHIR like ServiceRequest for parsing / uploading """
    RESOURCE_TYPE = 'ServiceRequest'

    def __init__(self):
        super().__init__()

    def search_url(self):
        """Generate the request path search url for ServiceRequest

        NB - this method does NOT invoke a round trip ID lookup.
        Call self.id() beforehand to force a lookup.
        """
        if self._id:
            return f"{self.RESOURCE_TYPE}/{self._id}"

        first_code = self._fields['code']['coding'][0]
        search_params = {
            "subject": self._fields["subject"]["reference"],
            "code": '|'.join((first_code["system"], first_code["code"])),
            "authored": self._fields["authoredOn"],
        }
        return f"{self.RESOURCE_TYPE}/?{urlencode(search_params)}"

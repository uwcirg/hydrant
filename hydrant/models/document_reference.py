from urllib.parse import urlencode

from hydrant.models.resource import Resource

CONTROLLED_SUBSTANCE_AGREEMENT_CODE = {
    'system': "https://loinc.org",
    'code': "94136-9",
    'display': "Controlled substance agreement"
}


class DocumentReference(Resource):
    """Minimal FHIR like DocumentReference for parsing / uploading """
    RESOURCE_TYPE = 'DocumentReference'

    def __init__(self):
        super().__init__()
        self._fields['status'] = 'current'

    def search_url(self):
        """Generate the request path search url for DocumentReference

        NB - this method does NOT invoke a round trip ID lookup.
        Call self.id() beforehand to force a lookup.
        """
        if self._id:
            return f"{self.RESOURCE_TYPE}/{self._id}"

        first_type = self._fields['type']['coding'][0]
        search_params = {
            "subject": self._fields["subject"]["reference"],
            "type": '|'.join((first_type["system"], first_type["code"])),
            "date": self._fields["date"],
        }
        return f"{self.RESOURCE_TYPE}/?{urlencode(search_params)}"

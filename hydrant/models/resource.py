from collections import OrderedDict
import requests

from hydrant.config import FHIR_SERVER_URL


class Resource(object):
    """Abstract Base class for FHIR resources"""

    def __init__(self):
        self._fields = OrderedDict()
        self._id = None

    def __repr__(self):
        if self._id is not None:
            return f"<{self.RESOURCE_TYPE} {self._id}>"
        else:
            return f"<{self.RESOURCE_TYPE}>"

    def id(self):
        """Look up FHIR id or return None if not found"""
        if self._id is not None:
            return self._id

        # Round-trip to see if this represents a new or existing resource
        if FHIR_SERVER_URL:
            headers = {'Cache-Control': 'no-cache'}
            response = requests.get('/'.join((FHIR_SERVER_URL, self.search_url())), headers=headers)
            response.raise_for_status()

            # extract Resource.id from bundle
            bundle = response.json()
            if bundle['total']:
                if bundle['total'] > 1:
                    raise RuntimeError(
                        "Found multiple matches, can't generate upsert"
                        f"for {self.search_url()}")
                assert bundle['entry'][0]['resource']['resourceType'] == self.RESOURCE_TYPE
                self._id = bundle['entry'][0]['resource']['id']
        return self._id

    def as_fhir(self):
        results = {'resourceType': self.RESOURCE_TYPE}
        results.update(self._fields)
        return results

    def as_upsert_entry(self):
        """Generate FHIR for inclusion in transaction bundle

        Transaction bundles need search and method details for
        FHIR server to perform requested task.

        :returns: JSON snippet to include in transaction bundle
        """
        results = {
            'resource': self.as_fhir(),
            'request': {
                # with conditional updates, always use "PUT"
                # 'method': "PUT" if self.id() else "POST",
                'method': "PUT",
                'url': self.search_url()}}
        return results

    @classmethod
    def factory(cls, data, adapter_cls):
        """Using parser API, pull available resource fields

        :param data: single `row` of data, from parsed file or db
        :param adapter_cls: class to be instantiated on `data` with
          accessor methods to obtain resource attributes from given
          format.

        :returns: populated resource instance, from parsed data
        """

        # Use given adapter to parse "row" data
        adapter = adapter_cls(data)

        # Populate instance with available data from adapter / row
        resource = cls()
        for key, value in adapter.items():
            if not value:
                continue
            resource._fields[key] = value

        return resource


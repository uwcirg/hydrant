import logging
from datetime import datetime
import requests

from hydrant.audit import audit_entry


class Bundle(object):
    """Minimal abstraction to build a FHIR complaint Bundle
    """
    template = {
      "resourceType": "Bundle",
      "meta": {
        "lastUpdated": datetime.utcnow().isoformat()
      },
      "type": "transaction",
      "total": 0,
    }

    def __init__(self, id='searchset', bundle_type='searchset', link=None):
        """Initialized bundle with known values

        :param id: Arbitrary id included at like top level attribute name
        :param bundle_type: Use for (reserved word) `type` for top level
          attribute name
        :param link: Can be a list of dictionaries defining `relation` and `url`
        """
        self.entries = []
        self.id = id
        self.bundle_type = bundle_type
        self.link = link or []

    def __len__(self):
        return len(self.entries)

    def add_entry(self, entry_or_resource):
        """Add entry to bundle

        :param entry_or_resource: a full bundle entry (i.e contains
          `fullUrl`, `resource`, `search`), or a FHIR resource to be
          added as a valid FHIR 'entry'.
        """
        def validate_resource_type(data):
            if 'resourceType' not in data:
                raise ValueError(f"ill formed bundle entry: {data}")

        if 'resource' not in entry_or_resource:
            # Bundles nest each entry under a 'resource'
            validate_resource_type(entry_or_resource)
            entry = {'resource': entry_or_resource}
        else:
            validate_resource_type(entry_or_resource['resource'])
            entry = entry_or_resource

        self.entries.append(entry)

    def as_fhir(self):
        results = self.template
        results.update({'entry': self.entries})
        results.update({'total': len(self.entries)})
        return results


class BatchUpload(object):
    """Upload a series of Bundles"""

    def __init__(self, target_system, batch_size=20):
        self.bundle = Bundle()
        self.target_system = target_system
        self.batch_size = batch_size
        self.total_sent = 0

    def add_entry(self, item):
        self.bundle.add_entry(item)
        if len(self.bundle) >= self.batch_size:
            self.transmit_bundle()

    def process(self, resources):
        for r in resources:
            self.add_entry(r.as_upsert_entry())
        # catch the last bundle not yet sent
        self.transmit_bundle()

    def transmit_bundle(self):
        if len(self.bundle) == 0:
            return

        fhir_bundle = self.bundle.as_fhir()
        logging.info(f"  - uploading next bundle to {self.target_system}")
        response = requests.post(self.target_system, json=fhir_bundle)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            # at least one item in the bundle generated an error
            audit_entry(f"response: {response.json()['issue']}", level="error")
            audit_entry(f"fhir_bundle which generated errors: {fhir_bundle}")
            raise http_err

        self.total_sent += len(self.bundle)
        extra = {'tags': ['upload'], 'system': self.target_system, 'user': 'system'}
        audit_entry(f"uploaded: {response.json()}", extra=extra)

        # reset internal state for next bundle
        self.bundle = Bundle()

from datetime import datetime


class Bundle(object):
    """Minimal abstraction to build a FHIR complaint Bundle
    """
    template = {
      "resourceType": "Bundle",
      "id": None,
      "meta": {
        "lastUpdated": datetime.utcnow()
      },
      "type": "searchset",
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

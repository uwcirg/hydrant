
class ResourceList(object):
    """Holds (ordered) list of FHIR Resources"""

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

            self.items.append(self.adapter.RESOURCE_CLASS.factory(row, self.adapter))

    def __iter__(self):
        if self.items is None:
            self._parse()

        for i in self.items:
            yield i

    def __len__(self):
        if self.items is None:
            self._parse()

        return len(self.items) if self.items else 0

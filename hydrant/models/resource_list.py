import logging


class ResourceList(object):
    """Generates unique FHIR Resources from given parser / adapter"""

    def __init__(self, parser, adapter):
        self.parser = parser
        self.adapter = adapter
        self.item_count = 0
        self._iteration_complete = False

    def __iter__(self):
        """Use parser and adapter, yield each unique resource"""
        keys_seen = set()
        for row in self.parser.rows():
            # Adapter may define unique_key() - if defined and a previous
            # entry matches, skip over this "duplicate"
            if hasattr(self.adapter, 'unique_key'):
                key = self.adapter(row).unique_key()
                if key in keys_seen:
                    logging.info("skipping duplicate: {key}")
                    continue
                keys_seen.add(key)

            self.item_count += 1
            yield self.adapter.RESOURCE_CLASS.factory(row, self.adapter)
        self._iteration_complete = True

    def __len__(self):
        """Return length (count) of unique resources discovered in generator

        NB: as a generator class, the full length is only known after iteration
        has been exhausted.  Therefore, this raises if iteration hasn't yet
        occurred.
        """
        if not self._iteration_complete:
            raise RuntimeError("request for generator length before complete iteration")
        return self.item_count

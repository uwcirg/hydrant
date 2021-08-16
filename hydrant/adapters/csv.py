import csv


class CSV_Parser(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._headers = None

    @property
    def headers(self):
        if self._headers:
            return self._headers

        with open(self.filepath, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            self._headers = [field for field in reader.fieldnames]
        return self._headers

    def rows(self):
        with open(self.filepath, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                yield row

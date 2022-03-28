import csv


class CSV_Serializer(object):
    def __init__(self, buffer):
        """Provide buffer (open file, stdout, stringIO) to receive serial data"""
        self._io = buffer
        self._headers = None
        self._headers_written = False
        self._buffer = []

    def headers(self, col_headers):
        self._headers = col_headers

    def add_row(self, row_data):
        self._buffer.append(row_data)

    def flush(self):
        if self._headers and not self._headers_written:
            self._io.write(','.join(self._headers) + '\n')
            self._headers_written = True

        for line in self._buffer:
            self._io.write(','.join(line) + '\n')
        self._io.flush()
        self._buffer = []


class CSV_Parser(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._headers = None
        self.csv_dialect = None

    @property
    def headers(self):
        if self._headers:
            return self._headers

        with open(self.filepath, 'r') as csv_file:
            if not self.csv_dialect:
                self.csv_dialect = csv.Sniffer().sniff(csv_file.read(1024))
                csv_file.seek(0)
            reader = csv.DictReader(csv_file, dialect=self.csv_dialect)
            self._headers = [field for field in reader.fieldnames]
        return self._headers

    def rows(self):
        with open(self.filepath, 'r') as csv_file:
            if not self.csv_dialect:
                self.csv_dialect = csv.Sniffer().sniff(csv_file.read(1024))
                csv_file.seek(0)
            reader = csv.DictReader(csv_file, dialect=self.csv_dialect)
            for row in reader:
                yield row

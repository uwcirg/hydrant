import xlrd


class ExcelParser(object):
    """Adapter to read data directly from Excel Workbooks"""
    def __init__(self, workbook_path):
        self.workbook = xlrd.open_workbook(workbook_path)
        self.reset()

    def reset(self):
        self.header = {}
        self.rows = []

    def parse_sheet(self, index=0):
        """Parse given sheet

        Populates internal header and row data.
        """
        if self.header or self.rows:
            raise ValueError(
                "Parsing over top of populated values; "
                "call purge() to reuse parser on second sheet")

        worksheet = self.workbook.sheet_by_index(index)
        for i, row in enumerate(range(worksheet.nrows)):
            if i == 0:
                for j, col in enumerate(range(worksheet.ncols)):
                    # build mapping of header value to col index
                    self.header[(worksheet.cell_value(i, j))] = i
            else:
                r = []
                for j, col in enumerate(range(worksheet.ncols)):
                    r.append(worksheet.cell_value(i, j))
                self.rows.append(r)

import unittest
from io import BytesIO

from openpyxl import Workbook

from app.import_parser import parse_xlsx_rows


class ImportParserTests(unittest.TestCase):
    def test_parse_single_data_row(self):
        workbook = Workbook()
        sheet = workbook.active
        assert sheet is not None
        sheet.append(["order_id", "customer_name", "delivery_date"])
        sheet.append(["RET-1", "A. Müller", "2026-08-03"])
        buffer = BytesIO()
        workbook.save(buffer)

        rows = parse_xlsx_rows(buffer.getvalue())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["order_id"], "RET-1")
        self.assertEqual(rows[0]["customer_name"], "A. Müller")
        self.assertEqual(rows[0]["delivery_date"], "2026-08-03")

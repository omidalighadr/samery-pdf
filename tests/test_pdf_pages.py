import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stderr
from io import StringIO

from pypdfium2 import PdfDocument

from pdf_pages import main


class PDFPagesTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.first = self.make_pdf("first.pdf", [100, 200, 300])
        self.second = self.make_pdf("second.pdf", [400])
        self.output = self.root / "result.pdf"

    def make_pdf(self, filename, widths):
        path = self.root / filename
        with PdfDocument.new() as pdf:
            for width in widths:
                pdf.new_page(width, 500).close()
            pdf.save(path)
        return path

    def widths(self):
        with PdfDocument(self.output) as pdf:
            return [pdf.get_page_size(i)[0] for i in range(len(pdf))]

    def test_merge_preserves_input_order(self):
        self.assertEqual(main(["merge", str(self.second), str(self.first), "-o", str(self.output)]), 0)
        self.assertEqual(self.widths(), [400, 100, 200, 300])

    def test_extract_includes_both_endpoints(self):
        self.assertEqual(main(["extract", str(self.first), "2-3", "-o", str(self.output)]), 0)
        self.assertEqual(self.widths(), [200, 300])

    def test_out_of_range_creates_no_output(self):
        with redirect_stderr(StringIO()):
            self.assertEqual(main(["extract", str(self.first), "2-4", "-o", str(self.output)]), 1)
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.output.write_bytes(b"existing")
        with redirect_stderr(StringIO()):
            self.assertEqual(main(["merge", str(self.first), "-o", str(self.output)]), 1)
        self.assertEqual(self.output.read_bytes(), b"existing")

    def test_invalid_later_input_keeps_sources_and_creates_no_output(self):
        invalid = self.root / "invalid.pdf"
        invalid.write_bytes(b"not a PDF")
        first_before = self.first.read_bytes()
        error = StringIO()

        with redirect_stderr(error):
            result = main(["merge", str(self.first), str(invalid), "-o", str(self.output)])

        self.assertEqual(result, 1)
        self.assertIn("Could not write PDF", error.getvalue())
        self.assertFalse(self.output.exists())
        self.assertEqual(self.first.read_bytes(), first_before)
        self.assertEqual(invalid.read_bytes(), b"not a PDF")
        self.assertEqual(
            {path.name for path in self.root.iterdir()},
            {"first.pdf", "second.pdf", "invalid.pdf"},
        )

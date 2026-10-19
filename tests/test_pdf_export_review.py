"""Preview approval must follow the exact PDF bytes and current options."""
import tempfile
import unittest
from pathlib import Path
from pypdf import PdfWriter

from pdf_export_review import review_pdf_inputs
from windows_app import check_pdf_input, check_page_count, parse_pages


class PdfReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.first = self.root / "a.pdf"
        self.second = self.root / "b.pdf"
        for file in (self.first, self.second):
            writer = PdfWriter()
            writer.add_blank_page(width=300, height=400)
            with file.open("wb") as fp:
                writer.write(fp)

    def review(self, paths=None, action="Remove metadata / select pages",
               pages="", password=""):
        return review_pdf_inputs(
            paths or [self.first], action, pages, password,
            check_pdf_input=check_pdf_input, check_page_count=check_page_count,
            parse_pages=parse_pages)

    def test_preview_does_not_create_outputs(self):
        before = set(self.root.iterdir())
        revision, label = self.review()
        self.assertEqual(revision, self.review()[0])
        self.assertIn("1", label)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_operation_or_file_contents_invalidate_preview(self):
        previous = self.review()[0]
        self.assertNotEqual(previous, self.review(pages="1")[0])
        self.assertNotEqual(previous,
                            self.review([self.first, self.second],
                                        "Merge selected PDFs")[0])
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=400)
        writer.add_blank_page(width=300, height=400)
        with self.first.open("wb") as fh:
            writer.write(fh)
        self.assertNotEqual(previous, self.review()[0])

    def test_bad_pages_and_missing_file_rejected(self):
        with self.assertRaises(ValueError):
            self.review(pages="0")
        with self.assertRaises((OSError, ValueError)):
            self.review([self.root / "missing.pdf"])


if __name__ == "__main__":
    unittest.main()

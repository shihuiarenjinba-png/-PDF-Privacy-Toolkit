"""Focused release-blocking PDF safety regressions. No confidential fixtures."""
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from windows_app import parse_pages, sanitize_pdf, split_pdf, merge_pdfs, verify_written_pdf


class PdfOutputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / "日本語 invoice.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=200)
        writer.add_blank_page(width=200, height=300)
        writer.add_metadata({"/Title": "private-title", "/Author": "private-author"})
        with self.src.open("wb") as handle:
            writer.write(handle)
        self.source_bytes = self.src.read_bytes()

    def test_strict_page_parser(self):
        self.assertEqual(parse_pages("", 3), [0, 1, 2])
        self.assertEqual(parse_pages("3,1-2,3", 3), [2, 0, 1])
        for spec in ("0", "4", "1,4", "1,,2", ",", "a", "1-foo", "1--3", "-1", "1.5"):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                parse_pages(spec, 3)
        with self.assertRaises(ValueError):
            parse_pages("", 0)

    def test_no_existing_export_can_be_replaced(self):
        out = self.root / "existing.pdf"
        out.write_bytes(b"prior valuable output")
        with self.assertRaises(FileExistsError):
            sanitize_pdf(self.src, out)
        self.assertEqual(out.read_bytes(), b"prior valuable output")
        self.assertEqual(self.src.read_bytes(), self.source_bytes)

    def test_metadata_and_page_count_are_verified(self):
        out = self.root / "out.pdf"
        sanitize_pdf(self.src, out, "2,1")
        verify_written_pdf(out, 2)
        reader = PdfReader(str(out), strict=True)
        self.assertEqual(len(reader.pages), 2)
        self.assertIsNone(reader.metadata)
        self.assertIsNone(reader.xmp_metadata)
        self.assertEqual(self.src.read_bytes(), self.source_bytes)

    def test_reject_empty_or_invalid_page_spec_without_output(self):
        out = self.root / "invalid.pdf"
        with self.assertRaises(ValueError):
            sanitize_pdf(self.src, out, "1,,2")
        self.assertFalse(out.exists())

    def test_split_preflights_all_destinations_before_writing(self):
        folder = self.root / "split"
        folder.mkdir()
        second = folder / f"{self.src.stem}_page_002.pdf"
        second.write_bytes(b"precious")
        with self.assertRaises(FileExistsError):
            split_pdf(self.src, folder)
        self.assertEqual(second.read_bytes(), b"precious")
        self.assertFalse((folder / f"{self.src.stem}_page_001.pdf").exists())

    def test_split_merge_and_encrypted_output(self):
        folder = self.root / "split2"
        self.assertEqual(split_pdf(self.src, folder), 2)
        inputs = sorted(folder.glob("*.pdf"))
        self.assertEqual(len(inputs), 2)
        for file in inputs:
            verify_written_pdf(file, 1)
        out = self.root / "merged-encrypted.pdf"
        merge_pdfs(inputs, out, password="private-local-password")
        encrypted = PdfReader(str(out))
        self.assertTrue(encrypted.is_encrypted)
        self.assertTrue(encrypted.decrypt("private-local-password"))
        self.assertEqual(len(encrypted.pages), 2)
        self.assertEqual(self.src.read_bytes(), self.source_bytes)

    def test_reject_encrypted_source(self):
        encrypted = self.root / "source-encrypted.pdf"
        w = PdfWriter()
        w.add_blank_page(width=100, height=100)
        w.encrypt("authorized")
        with encrypted.open("wb") as stream:
            w.write(stream)
        out = self.root / "should-not-exist.pdf"
        with self.assertRaises(ValueError):
            sanitize_pdf(encrypted, out)
        self.assertFalse(out.exists())

    def test_reject_corrupt_source(self):
        corrupt = self.root / "corrupt.pdf"
        corrupt.write_bytes(b"%PDF-1.5\ncorrupted")
        target = self.root / "corrupt-out.pdf"
        with self.assertRaises(Exception):
            sanitize_pdf(corrupt, target)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()

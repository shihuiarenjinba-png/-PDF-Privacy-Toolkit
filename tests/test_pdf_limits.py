import tempfile
import unittest
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from windows_app import check_pdf_input, check_page_count, merge_pdfs


class PdfLimitTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
    def test_empty_input_rejected(self):
        p=self.root/'empty.pdf'
        p.write_bytes(b'')
        with self.assertRaisesRegex(ValueError,'empty'):
            check_pdf_input(p)
    def test_large_sparse_input_rejected(self):
        p=self.root/'large.pdf'
        with p.open('wb') as f:
            f.truncate(65*1024*1024)
        with self.assertRaisesRegex(ValueError,'64 MiB'):
            check_pdf_input(p)
    def test_normal_pdf_accepted(self):
        p=self.root/'normal.pdf'
        w=PdfWriter()
        w.add_blank_page(width=200,height=200)
        with p.open('wb') as f:w.write(f)
        check_pdf_input(p)
        check_page_count(PdfReader(str(p)))
    def test_501_pages_rejected(self):
        p=self.root/'many.pdf'
        w=PdfWriter()
        for _ in range(501):
            w.add_blank_page(width=200,height=200)
        with p.open('wb') as f:w.write(f)
        with self.assertRaisesRegex(ValueError,'500 page'):
            check_page_count(PdfReader(str(p)))
    def test_merge_file_count_limit(self):
        with self.assertRaisesRegex(ValueError,'2–20'):
            merge_pdfs([self.root/f'{x}.pdf' for x in range(21)],self.root/'out.pdf')
        self.assertFalse((self.root/'out.pdf').exists())


if __name__=='__main__':
    unittest.main()

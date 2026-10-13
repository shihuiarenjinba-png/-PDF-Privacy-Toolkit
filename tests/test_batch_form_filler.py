"""Offline form-filling regression tests. Requires pypdf, openpyxl, reportlab."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader
from reportlab.pdfgen import canvas

from batch_form_filler import batch_fill, records


def make_form(path: Path) -> None:
    c = canvas.Canvas(str(path))
    c.drawString(45, 760, "Name:")
    c.acroForm.textfield(name="name", tooltip="name", x=100, y=748, width=220, height=24)
    c.drawString(45, 710, "Amount:")
    c.acroForm.textfield(name="amount", tooltip="amount", x=100, y=698, width=220, height=24)
    c.save()


def make_csv(path: Path, rows: list[list[str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerows([["person_name", "yen"]] + rows)


class BatchFormFillerTest(unittest.TestCase):
    def test_fill_two_rows_and_no_original_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            form, data = root / "form.pdf", root / "data.csv"
            make_form(form)
            make_csv(data, [["Alice", "100"], ["Bob", "200"]])
            before = form.read_bytes()
            result = batch_fill(form, data, root / "reports",
                                {"name": "person_name", "amount": "yen"})
            self.assertEqual(form.read_bytes(), before)
            report = json.loads((result / "batch_report.json").read_text(encoding="utf-8"))
            self.assertEqual(len(report["files"]), 2)
            self.assertTrue(all(i["status"] == "FIELD_VALUES_VERIFIED" for i in report["files"]))
            self.assertEqual(PdfReader(result / "filled_0001.pdf").get_fields()["name"]["/V"], "Alice")
            self.assertEqual(PdfReader(result / "filled_0002.pdf").get_fields()["amount"]["/V"], "200")

    def test_unknown_mapping_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            form, data = root / "form.pdf", root / "data.csv"
            make_form(form)
            make_csv(data, [["Alice", "100"]])
            with self.assertRaises(ValueError):
                batch_fill(form, data, root / "out", {"unknown": "person_name"})

    def test_japanese_text_requires_visual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            form, data = root / "form.pdf", root / "data.csv"
            make_form(form)
            make_csv(data, [["山田太郎", "300"]])
            folder = batch_fill(form, data, root / "out", {"name": "person_name"})
            report = json.loads((folder / "batch_report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["files"][0]["non_ascii_font_review"])
            self.assertEqual(report["files"][0]["status"], "REVIEW")

    def test_duplicate_headers_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.csv"
            path.write_text("id,id\n1,2\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                records(path)


if __name__ == "__main__":
    unittest.main()

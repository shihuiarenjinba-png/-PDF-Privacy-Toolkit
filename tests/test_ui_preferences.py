import json
import tempfile
import unittest
from pathlib import Path

from ui_preferences import load_preferences, save_preferences, preference_path


class PreferencesTests(unittest.TestCase):
    def test_roundtrip_japanese_and_versioned_format(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            values = {"output": "C:\\QA\\日本語プロジェクト\\001"}
            target = save_preferences("PDFBatchForms", values, ("output",), override_dir=root)
            self.assertEqual(target, root / "preferences.json")
            self.assertEqual(load_preferences("PDFBatchForms", ("output",), override_dir=root), values)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["schema_version"], 1)

    def test_unknown_field_rejected_without_mutating_saved_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = save_preferences("PDFBatchForms", {"output": "C:\\a"}, ("output",), override_dir=root)
            previous = target.read_bytes()
            with self.assertRaises(ValueError):
                save_preferences("PDFBatchForms", {"password": "secret"}, ("output",), override_dir=root)
            self.assertEqual(target.read_bytes(), previous)

    def test_corruption_and_newer_schema_are_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = preference_path("PDFBatchForms", override_dir=root)
            target.write_text("{not-valid", encoding="utf-8")
            with self.assertRaises(ValueError):
                save_preferences("PDFBatchForms", {"output": "C:\\a"}, ("output",), override_dir=root)
            self.assertEqual(target.read_text(encoding="utf-8"), "{not-valid")
            target.write_text('{"schema_version":2,"values":{"output":"new"}}', encoding="utf-8")
            with self.assertRaises(ValueError):
                save_preferences("PDFBatchForms", {"output": "C:\\a"}, ("output",), override_dir=root)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["schema_version"], 2)

    def test_data_limit_and_invalid_product(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                save_preferences("PDFBatchForms", {"output": "a" * 5000}, ("output",), override_dir=Path(folder))
            with self.assertRaises(ValueError):
                preference_path("../other", override_dir=Path(folder))


if __name__ == "__main__":
    unittest.main()

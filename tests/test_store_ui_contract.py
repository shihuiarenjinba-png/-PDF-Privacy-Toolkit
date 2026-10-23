"""Static Store-facing UI contract.

This test protects the reviewed Store-facing title/layout/path-privacy decisions.
It does not replace real Windows 11 DPI or interaction QA.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = (ROOT / "windows_app.py").read_text(encoding="utf-8")
CHECKS = [["PDF Privacy — Windows","reserved Store window title"],["text=\"PDF Privacy\"","reserved Store heading"],["self.root.geometry(\"930x650\")","default geometry"],["self.root.minsize(820, 560)","minimum geometry"]]

class StoreUiContractTests(unittest.TestCase):
    def test_reviewed_ui_contract_is_present(self):
        for token, purpose in CHECKS:
            with self.subTest(purpose=purpose):
                self.assertIn(token, UI)

if __name__ == "__main__":
    unittest.main()

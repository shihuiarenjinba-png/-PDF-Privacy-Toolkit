from __future__ import annotations

import locale
import os
import tkinter as tk
from tkinter import filedialog, messagebox

_LANGUAGE = "ja" if any((x or "").lower().startswith("ja") for x in (locale.getlocale()[0], os.environ.get("LANG"))) else "en"
_CONTROLLERS = []
_PATCHED = False

TEXTS = {
    "PDF Privacy Toolkit": ("PDF Privacy Toolkit", "PDFプライバシーツールキット"),
    "PDF Privacy Toolkit — Windows": ("PDF Privacy Toolkit — Windows", "PDFプライバシーツールキット — Windows"),
    "Merge, split, reorder/delete pages, remove document/XMP metadata, and optionally AES-256-R5 password-protect PDFs locally.": ("Merge, split, reorder/delete pages, remove document/XMP metadata, and optionally AES-256-R5 password-protect PDFs locally.", "PDFの結合・分割・ページ並べ替え/削除・文書/XMPメタデータ削除・AES-256-R5パスワード保護をローカルで行います。"),
    "Add PDFs": ("Add PDFs", "PDFを追加"),
    "Sanitize first": ("Sanitize first", "先頭PDFを安全化"),
    "Split first": ("Split first", "先頭PDFを分割"),
    "Merge all": ("Merge all", "すべて結合"),
    "Pages to keep/order for Sanitize (example: 1,3-5,2; blank = all):": ("Pages to keep/order for Sanitize (example: 1,3-5,2; blank = all):", "安全化で残す/並べるページ（例: 1,3-5,2、空欄=すべて）:"),
    "Optional output password (AES-256-R5):": ("Optional output password (AES-256-R5):", "任意の出力パスワード (AES-256-R5):"),
    "Select PDFs": ("Select PDFs", "PDFを選択"),
    "Choose split output folder": ("Choose split output folder", "分割出力フォルダを選択"),
    "Add a PDF first.": ("Add a PDF first.", "先にPDFを追加してください。"),
    "Add at least two PDFs to merge.": ("Add at least two PDFs to merge.", "結合するPDFを2つ以上追加してください。"),
    "PDF": ("PDF", "PDF"),
}

PHRASES = (
    ("Page out of range", "ページ範囲外"),
    ("Encrypted PDFs are not modified by this MVP. Decrypt with authorization before processing.", "暗号化PDFは変更しません。権限を確認して復号してから処理してください。"),
    ("Encrypted PDFs are not modified by this MVP.", "暗号化PDFは変更しません。"),
    ("Encrypted PDF cannot be merged by this MVP", "暗号化PDFは結合できません"),
    ("Refusing to overwrite an input PDF", "入力PDFの上書きを拒否しました"),
    ("Refusing to overwrite an input file", "入力ファイルの上書きを拒否しました"),
    ("Saved:", "保存しました:"),
    ("Created ", "作成: "),
    ("metadata-clean page PDFs", "メタデータを除去したページPDF"),
    ("not encrypted", "未暗号化"),
    ("encrypted", "暗号化"),
    ("pages", "ページ"),
    ("ERROR", "エラー"),
)


def get_language() -> str:
    return _LANGUAGE


def translate(text):
    if not isinstance(text, str):
        return text
    if text in TEXTS:
        return TEXTS[text][1 if _LANGUAGE == "ja" else 0]
    if _LANGUAGE == "ja":
        for en, ja in PHRASES:
            text = text.replace(en, ja)
    return text


def set_language(lang: str):
    global _LANGUAGE
    if lang not in {"en", "ja"}:
        raise ValueError("language must be 'en' or 'ja'")
    _LANGUAGE = lang
    for controller in tuple(_CONTROLLERS):
        controller.refresh()


def _patch():
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True
    original_insert = tk.Listbox.insert
    tk.Listbox.insert = lambda self, index, *items: original_insert(self, index, *(translate(x) for x in items))
    for name in ("showinfo", "showwarning", "showerror"):
        original = getattr(messagebox, name)
        setattr(messagebox, name, lambda title, message, *a, _f=original, **k: _f(translate(title), translate(message), *a, **k))
    for name in ("askopenfilename", "askopenfilenames", "asksaveasfilename", "askdirectory"):
        original = getattr(filedialog, name)
        def wrapper(*a, _f=original, **k):
            if "title" in k:
                k["title"] = translate(k["title"])
            if "filetypes" in k:
                k["filetypes"] = [(translate(label), pattern) for label, pattern in k["filetypes"]]
            return _f(*a, **k)
        setattr(filedialog, name, wrapper)


class LanguageController:
    def __init__(self, root):
        self.root = root
        self.original_title = root.title()
        self._snapshot(root)
        frame = tk.Frame(root, padx=12, pady=6)
        frame.pack(fill="x")
        self.button = tk.Button(frame, width=12, command=self.toggle)
        self.button.pack(side="right")
        _CONTROLLERS.append(self)
        self.refresh()

    def _snapshot(self, widget):
        try:
            widget._i18n_original_text = widget.cget("text")
        except Exception:
            pass
        for child in widget.winfo_children():
            self._snapshot(child)

    def _refresh(self, widget):
        if widget is not self.button and hasattr(widget, "_i18n_original_text"):
            try:
                widget.configure(text=translate(widget._i18n_original_text))
            except Exception:
                pass
        for child in widget.winfo_children():
            self._refresh(child)

    def refresh(self):
        self.root.title(translate(self.original_title))
        self._refresh(self.root)
        self.button.configure(text="English" if _LANGUAGE == "ja" else "日本語")

    def toggle(self):
        set_language("en" if _LANGUAGE == "ja" else "ja")


def install_bilingual_ui(root):
    _patch()
    return LanguageController(root)

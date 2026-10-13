"""Minimal offline Windows GUI for batch_form_filler.py.

Requires pypdf; openpyxl for XLSX. JSON mapping is optional.
"""
from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader
from batch_form_filler import batch_fill, _form_fields, records


class FormBatchGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PDF帳票の一括入力（試作版）")
        self.geometry("850x540")
        self.minsize(710, 470)
        self.template = tk.StringVar()
        self.data = tk.StringVar()
        self.mapping = tk.StringVar()
        self.output = tk.StringVar(value=str(Path.home() / "Documents"))
        self.status = tk.StringVar(value="入力可能なテキストフォームを持つPDFテンプレートとCSV/XLSXを選択してください。")
        body = ttk.Frame(self, padding=18)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        ttk.Label(body, text="定型PDFの一括入力", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
        self._pick_row(body, 1, "PDFテンプレート", self.template, (("PDF", "*.pdf"),))
        self._pick_row(body, 2, "CSV / Excel", self.data, (("Data", "*.csv *.xlsx"),))
        self._pick_row(body, 3, "列名対応JSON（任意）", self.mapping, (("JSON", "*.json"),))
        self._pick_row(body, 4, "出力フォルダ", self.output, directory=True)
        ttk.Button(body, text="テンプレート欄とCSV列名を確認", command=self.inspect).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(10, 8))
        self.preview = tk.Text(body, height=11, width=75, wrap="word", state="disabled")
        self.preview.grid(row=6, column=0, columnspan=3, sticky="nsew")
        body.rowconfigure(6, weight=1)
        ttk.Label(body, text="日本語などの非ASCII文字はPDF表示崩れの可能性があるため、出力後に目視確認してください。",
                  wraplength=790).grid(row=7, column=0, columnspan=3, sticky="w", pady=8)
        ttk.Button(body, text="一括生成（元PDFは変更しません）", command=self.run_fill).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=10)
        ttk.Label(body, textvariable=self.status, wraplength=790).grid(
            row=9, column=0, columnspan=3, sticky="w")

    def _pick_row(self, parent, row, label, variable, types=None, directory=False) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", pady=5)
        def select() -> None:
            p = filedialog.askdirectory() if directory else filedialog.askopenfilename(
                filetypes=types or [("All", "*.*")])
            if p:
                variable.set(p)
        ttk.Button(parent, text="参照", command=select).grid(row=row, column=2, padx=(6, 0))

    def inspect(self) -> None:
        try:
            fields = _form_fields(PdfReader(self.template.get()))
            headers, rows = records(Path(self.data.get()).expanduser().resolve())
            message = "PDFフィールド:\n" + ", ".join(fields)
            message += "\n\nデータ列名:\n" + ", ".join(headers)
            message += f"\n\nレコード数: {len(rows)}\n"
            self.preview.config(state="normal")
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", message)
            self.preview.config(state="disabled")
            self.status.set("列名が違う場合は、JSONファイルでPDFフィールド名とデータ列を対応させます。")
        except Exception as exc:
            messagebox.showerror("検査エラー", str(exc))

    def run_fill(self) -> None:
        try:
            mapping = None
            if self.mapping.get().strip():
                mapping = json.loads(Path(self.mapping.get()).read_text(encoding="utf-8"))
                if not isinstance(mapping, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()):
                    raise ValueError("対応JSONは文字列キーと文字列値の辞書形式にしてください")
            _headers, rows = records(Path(self.data.get()).expanduser().resolve())
            if len(rows) > 50 and not messagebox.askyesno(
                "一括生成の確認", f"{len(rows)}件のPDFを生成します。続行しますか？"):
                return
            result = batch_fill(self.template.get(), self.data.get(), self.output.get(), mapping)
            self.status.set(f"出力先: {result}")
            messagebox.showinfo("完了", f"出力先: {result}\n\n生成後、PDFの表示と値を必ず確認してください。")
        except Exception as exc:
            self.status.set(f"エラー: {exc}")
            messagebox.showerror("生成失敗", str(exc))



def _validation_smoke() -> None:
    """Noninteractive Tk widget construction smoke; not user-click testing."""
    import json
    import sys
    from pathlib import Path
    if len(sys.argv) != 4 or sys.argv[1] != "--smoke-test" or sys.argv[2] != "--smoke-output":
        raise SystemExit(2)
    app = FormBatchGUI()
    try:
        app.update_idletasks()
        app.update()
        assert app.winfo_exists() and app.title() and len(app.winfo_children()) > 0
        result = {"status": "GUI_PROCESS_SMOKE_OK", "title": app.title(),
                  "scope": "Tk initialization and event pump only; no simulated clicks"}
        with Path(sys.argv[3]).open("x", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False)
    finally:
        app.destroy()


if __name__ == "__main__":
    import sys
    if "--smoke-test" in sys.argv:
        _validation_smoke()
    else:
        FormBatchGUI().mainloop()

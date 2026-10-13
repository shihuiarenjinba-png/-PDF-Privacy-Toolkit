"""Synthetic PDF AcroForm GUI E2E using pypdf only (no reportlab in EXE).

This probes text-field correctness, UI preview, output bytes and bad mappings;
visual PDF glyph/font rendering still requires manual review.
"""
from __future__ import annotations
import csv
import json
import sys
import tempfile
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject as A, DictionaryObject as D, NameObject as N
from pypdf.generic import NumberObject as I, TextStringObject as T


def create_form(path):
    writer=PdfWriter()
    page=writer.add_blank_page(width=300,height=300)
    font=writer._add_object(D({N("/Type"):N("/Font"),N("/Subtype"):N("/Type1"),N("/BaseFont"):N("/Helvetica")}))
    resources=writer._add_object(D({N("/Font"):D({N("/Helv"):font})}))
    fields=[]
    for index,name in enumerate(("name","amount")):
        annotation=D({
            N("/FT"):N("/Tx"),N("/Type"):N("/Annot"),N("/Subtype"):N("/Widget"),
            N("/T"):T(name),N("/V"):T(""),N("/F"):I(4),
            N("/Rect"):A([I(30),I(250-40*index),I(220),I(270-40*index)]),
            N("/DA"):T("/Helv 12 Tf 0 g"),
        })
        fields.append(writer._add_object(annotation))
    page[N("/Annots")]=A(fields)
    writer._root_object[N("/AcroForm")]=writer._add_object(
        D({N("/Fields"):A(fields),N("/DR"):resources,N("/DA"):T("/Helv 12 Tf 0 g")}))
    writer.write(path)


def buttons(app, name):
    found=[]
    def visit(widget):
        for child in widget.winfo_children():
            if isinstance(child,ttk.Button) and child.cget("text")==name:
                found.append(child)
            visit(child)
    visit(app)
    return found


def run(GUI):
    if len(sys.argv)!=3 or sys.argv[1]!="--e2e-test":
        raise ValueError("Usage: --e2e-test <proof.json>")
    proof=Path(sys.argv[2]).resolve()
    with tempfile.TemporaryDirectory(prefix="pdf_form_gui_e2e_") as directory:
        root=Path(directory)
        form=root/"blank_form.pdf"
        csvpath=root/"records.csv"
        reports=root/"out"
        create_form(form)
        with csvpath.open("w",encoding="utf-8",newline="") as f:
            writer=csv.writer(f)
            writer.writerow(["name","amount"])
            writer.writerows([["Alice","100"],["Bob","200"]])
        original=(form.read_bytes(),csvpath.read_bytes())
        app=GUI()
        errors=[]
        infos=[]
        try:
            app.withdraw()
            app.update()
            browse=buttons(app,"参照")
            assert len(browse)==4
            with patch.object(filedialog,"askopenfilename",return_value=str(form)):
                browse[0].invoke()
            with patch.object(filedialog,"askopenfilename",return_value=str(csvpath)):
                browse[1].invoke()
            with patch.object(filedialog,"askdirectory",return_value=str(reports)):
                browse[3].invoke()
            assert app.template.get()==str(form)
            assert app.data.get()==str(csvpath)
            assert app.output.get()==str(reports)
            with patch.object(messagebox,"showinfo",side_effect=lambda *args: infos.append(args)), \
                 patch.object(messagebox,"showerror",side_effect=lambda *args: errors.append(args)):
                preview=buttons(app,"テンプレート欄とCSV列名を確認")
                assert len(preview)==1
                preview[0].invoke()
                txt=app.preview.get("1.0","end")
                assert "name" in txt and "amount" in txt and "2" in txt, txt
                fill=buttons(app,"一括生成（元PDFは変更しません）")
                assert len(fill)==1
                fill[0].invoke()
                outputs=list(reports.glob("batch_pdf_forms_*/batch_report.json"))
                assert len(outputs)==1, outputs
                report=json.loads(outputs[0].read_text(encoding="utf-8"))
                folder=outputs[0].parent
                assert len(report["files"])==2
                for i,(name,amount) in enumerate([("Alice","100"),("Bob","200")],start=1):
                    pdf=folder/f"filled_{i:04d}.pdf"
                    assert pdf.exists()
                    fields=PdfReader(pdf).get_fields()
                    assert fields["name"]["/V"]==name and fields["amount"]["/V"]==amount
                assert form.read_bytes()==original[0] and csvpath.read_bytes()==original[1]
                assert infos and not errors,errors
                # Malformed mapping must display an error rather than generate another batch.
                invalid=root/"bad_mapping.json"
                invalid.write_text(json.dumps({"unknown":"name"}),encoding="utf-8")
                with patch.object(filedialog,"askopenfilename",return_value=str(invalid)):
                    browse[2].invoke()
                fill[0].invoke()
                assert errors, "Invalid mapping was silently accepted"
                assert len(list(reports.glob("batch_pdf_forms_*/batch_report.json")))==1
            with proof.open("x",encoding="utf-8") as out:
                json.dump({"status":"GUI_E2E_OK","scenario":"select form -> preview -> batch fill -> verify fields -> reject bad mapping",
                           "actual_output_verified":True,"input_unchanged":True,
                           "negative_case_verified":True,"interactive_human_test":False,
                           "font_render_verified":False},out,ensure_ascii=False,indent=2)
        finally:
            app.destroy()

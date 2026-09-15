from pathlib import Path
import tempfile
from pypdf import PdfReader, PdfWriter

from windows_app import sanitize_pdf, split_pdf, merge_pdfs

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    src = root / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    writer.add_metadata({"/Title": "secret"})
    with src.open("wb") as fh:
        writer.write(fh)

    clean = root / "clean.pdf"
    sanitize_pdf(src, clean, "2,1")
    reader = PdfReader(str(clean))
    assert len(reader.pages) == 2

    split_dir = root / "split"
    assert split_pdf(src, split_dir) == 2
    merged = root / "merged.pdf"
    merge_pdfs([split_dir / "sample_page_001.pdf", split_dir / "sample_page_002.pdf"], merged)
    assert len(PdfReader(str(merged)).pages) == 2
print("PDF Privacy Toolkit smoke test: OK")

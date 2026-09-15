from pathlib import Path
import tempfile
from pypdf import PdfReader, PdfWriter

from windows_app import sanitize_pdf, split_pdf, merge_pdfs

XMP = b'''<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title><rdf:Alt><rdf:li xml:lang="x-default">secret</rdf:li></rdf:Alt></dc:title>
</rdf:Description></rdf:RDF></x:xmpmeta>
<?xpacket end="w"?>'''


def assert_metadata_clean(path: Path) -> None:
    reader = PdfReader(str(path))
    assert reader.metadata is None, reader.metadata
    assert reader.xmp_metadata is None, reader.xmp_metadata


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    src = root / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_blank_page(width=200, height=200)
    writer.add_metadata({"/Title": "secret", "/Author": "private"})
    writer.xmp_metadata = XMP
    with src.open("wb") as fh:
        writer.write(fh)

    source_reader = PdfReader(str(src))
    assert source_reader.metadata is not None
    assert source_reader.xmp_metadata is not None

    clean = root / "clean.pdf"
    sanitize_pdf(src, clean, "2,1")
    reader = PdfReader(str(clean))
    assert len(reader.pages) == 2
    assert_metadata_clean(clean)

    split_dir = root / "split"
    assert split_pdf(src, split_dir) == 2
    first = split_dir / "sample_page_001.pdf"
    second = split_dir / "sample_page_002.pdf"
    assert_metadata_clean(first)
    assert_metadata_clean(second)

    merged = root / "merged.pdf"
    merge_pdfs([first, second], merged)
    assert len(PdfReader(str(merged)).pages) == 2
    assert_metadata_clean(merged)

print("PDF Privacy Toolkit smoke test: OK")

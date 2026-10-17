from __future__ import annotations

from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Entry, Frame, Label, Listbox, StringVar, Tk, filedialog, messagebox

from pypdf import PdfReader, PdfWriter


def ensure_distinct_path(src: Path, out: Path) -> None:
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = src.absolute() == out.absolute()
    if same:
        raise ValueError("Refusing to overwrite the original PDF.")


def parse_pages(spec: str, total: int) -> list[int]:
    """Strictly parse unique, one-based page selections without empty outputs."""
    import re

    if total < 1:
        raise ValueError("Cannot process a PDF with no pages.")
    if not spec.strip():
        return list(range(total))
    result: list[int] = []
    seen: set[int] = set()
    if len(spec) > 20000:
        raise ValueError("Page selection is too long.")
    for token in spec.split(","):
        token = token.strip()
        if not re.fullmatch(r"[0-9]+(?:\s*-\s*[0-9]+)?", token):
            raise ValueError(f"Invalid page selection: {token[:60]!r}")
        bounds = [int(value.strip()) for value in token.split("-")]
        a, b = bounds if len(bounds) == 2 else (bounds[0], bounds[0])
        if a < 1 or b < 1 or a > total or b > total:
            raise ValueError(f"Page out of range: {token}")
        if a > b:
            a, b = b, a
        for idx in range(a - 1, b):
            if idx not in seen:
                seen.add(idx)
                result.append(idx)
    if not result:
        raise ValueError("No pages selected.")
    return result


def strip_writer_metadata(writer: PdfWriter) -> None:
    """Remove document-info/XMP only. This is NOT PDF content redaction."""
    writer.metadata = None
    writer.xmp_metadata = None
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)


def protect_writer(writer: PdfWriter, password: str) -> None:
    if password:
        writer.encrypt(password, algorithm="AES-256-R5")


def verify_written_pdf(out: Path, expected_pages: int, password: str = "", remove_metadata: bool = True) -> None:
    """Check the narrow properties we actually promise after writing."""
    checked = PdfReader(str(out), strict=True)
    if bool(password) != checked.is_encrypted:
        raise ValueError("Output encryption did not match the selected setting.")
    if password and not checked.decrypt(password):
        raise ValueError("Output password verification failed.")
    if len(checked.pages) != expected_pages:
        raise ValueError("Output page count verification failed.")
    if remove_metadata and (checked.metadata or checked.xmp_metadata):
        raise ValueError("Output document-info or XMP metadata remains.")


def _publish_writer(writer: PdfWriter, out: Path, expected_pages: int, password: str = "") -> None:
    # Exclusive creation: neither a source nor any existing export may be replaced.
    created = False
    try:
        with out.open("xb") as fh:
            created = True
            writer.write(fh)
        if out.stat().st_size <= 0:
            raise ValueError("Generated PDF is empty.")
        verify_written_pdf(out, expected_pages, password)
    except BaseException:
        if created:
            out.unlink(missing_ok=True)
        raise


def write_pdf(reader: PdfReader, pages: list[int], out: Path,
              remove_metadata: bool = True, password: str = "") -> None:
    if not pages:
        raise ValueError("Cannot export zero pages.")
    if out.exists() or out.is_symlink():
        raise FileExistsError("Output PDF already exists. Choose a new filename.")
    writer = PdfWriter()
    for idx in pages:
        writer.add_page(reader.pages[idx])
    if remove_metadata:
        strip_writer_metadata(writer)
    protect_writer(writer, password)
    _publish_writer(writer, out, len(pages), password)


def sanitize_pdf(src: Path, out: Path, page_spec: str = "", password: str = "") -> None:
    """Keep/reorder pages and remove *metadata*, not page text or secrets."""
    ensure_distinct_path(src, out)
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified. Supply an authorized decrypted copy.")
    pages = parse_pages(page_spec, len(reader.pages))
    write_pdf(reader, pages, out, remove_metadata=True, password=password)


def split_pdf(src: Path, output_dir: Path) -> int:
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified.")
    count = len(reader.pages)
    if count < 1:
        raise ValueError("Input PDF has no pages.")
    if output_dir.is_symlink():
        raise ValueError("Output directory cannot be a symlink.")
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = [output_dir / f"{src.stem}_page_{i+1:03d}.pdf" for i in range(count)]
    for target in targets:
        ensure_distinct_path(src, target)
        if target.exists() or target.is_symlink():
            raise FileExistsError(f"Split would replace an existing file: {target.name}")
    created: list[Path] = []
    try:
        for idx, target in enumerate(targets):
            write_pdf(reader, [idx], target, remove_metadata=True)
            created.append(target)
    except BaseException:
        for target in created:
            target.unlink(missing_ok=True)
        raise
    return count


def merge_pdfs(inputs: list[Path], out: Path, password: str = "") -> None:
    if len(inputs) < 2:
        raise ValueError("Select at least two PDFs to merge.")
    for src in inputs:
        ensure_distinct_path(src, out)
    if out.exists() or out.is_symlink():
        raise FileExistsError("Output PDF already exists. Choose a new filename.")
    writer = PdfWriter()
    total_pages = 0
    for src in inputs:
        reader = PdfReader(str(src), strict=True)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF cannot be merged: {src.name}")
        if not reader.pages:
            raise ValueError(f"PDF has no pages: {src.name}")
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1
    strip_writer_metadata(writer)
    protect_writer(writer, password)
    _publish_writer(writer, out, total_pages, password)


class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("PDF Privacy Toolkit — Windows")
        self.root.geometry("900x620")
        self.files: list[Path] = []
        self.pages = StringVar()
        self.password = StringVar()

        head = Frame(root, padx=12, pady=12)
        head.pack(fill="x")
        Label(head, text="PDF Privacy Toolkit", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(head, text="Merge, split, reorder/delete pages, remove document/XMP metadata, and optionally AES-256-R5 password-protect PDFs locally.").pack(anchor="w")

        controls = Frame(root, padx=12)
        controls.pack(fill="x")
        Button(controls, text="Add PDFs", width=15, command=self.add_files).pack(side=LEFT)
        Button(controls, text="Sanitize first", width=16, command=self.sanitize_first).pack(side=LEFT, padx=6)
        Button(controls, text="Split first", width=14, command=self.split_first).pack(side=LEFT)
        Button(controls, text="Merge all", width=14, command=self.merge_all).pack(side=LEFT, padx=6)

        opts = Frame(root, padx=12, pady=10)
        opts.pack(fill="x")
        Label(opts, text="Pages to keep/order for Sanitize (example: 1,3-5,2; blank = all):").pack(anchor="w")
        Entry(opts, textvariable=self.pages).pack(fill="x", pady=(2, 8))
        Label(opts, text="Optional output password (AES-256-R5):").pack(anchor="w")
        Entry(opts, textvariable=self.password, show="*").pack(fill="x")

        self.listbox = Listbox(root, font=("Consolas", 10))
        self.listbox.pack(fill=BOTH, expand=True, padx=12, pady=12)

    def add_files(self):
        for p in filedialog.askopenfilenames(parent=self.root, title="Select PDFs", filetypes=[("PDF", "*.pdf")]):
            path = Path(p)
            if path not in self.files:
                self.files.append(path)
        self.listbox.delete(0, END)
        for p in self.files:
            try:
                r = PdfReader(str(p), strict=True)
                encrypted = "encrypted" if r.is_encrypted else "not encrypted"
                info_meta = bool(r.metadata) if not r.is_encrypted else False
                xmp_meta = bool(r.xmp_metadata) if not r.is_encrypted else False
                self.listbox.insert(END, f"{p.name} | {len(r.pages) if not r.is_encrypted else '?'} pages | {encrypted} | info={info_meta} xmp={xmp_meta}")
            except Exception as exc:
                self.listbox.insert(END, f"ERROR {p.name}: {exc}")

    def sanitize_first(self):
        if not self.files:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add a PDF first.")
        out = filedialog.asksaveasfilename(parent=self.root, defaultextension=".pdf", initialfile=f"{self.files[0].stem}_clean.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        try:
            sanitize_pdf(self.files[0], Path(out), self.pages.get(), self.password.get())
            messagebox.showinfo("PDF Privacy Toolkit", f"Saved: {out}")
        except Exception as exc:
            messagebox.showerror("PDF Privacy Toolkit", str(exc))

    def split_first(self):
        if not self.files:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add a PDF first.")
        folder = filedialog.askdirectory(parent=self.root, title="Choose split output folder")
        if not folder:
            return
        try:
            count = split_pdf(self.files[0], Path(folder))
            messagebox.showinfo("PDF Privacy Toolkit", f"Created {count} metadata-clean page PDFs.")
        except Exception as exc:
            messagebox.showerror("PDF Privacy Toolkit", str(exc))

    def merge_all(self):
        if len(self.files) < 2:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add at least two PDFs to merge.")
        out = filedialog.asksaveasfilename(parent=self.root, defaultextension=".pdf", initialfile="merged_clean.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        try:
            merge_pdfs(self.files, Path(out), self.password.get())
            messagebox.showinfo("PDF Privacy Toolkit", f"Saved: {out}")
        except Exception as exc:
            messagebox.showerror("PDF Privacy Toolkit", str(exc))


def main():
    from i18n import install_bilingual_ui

    root = Tk()
    App(root)
    install_bilingual_ui(root)
    root.mainloop()


if __name__ == "__main__":
    main()

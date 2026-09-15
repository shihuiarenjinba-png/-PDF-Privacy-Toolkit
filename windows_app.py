from __future__ import annotations

from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Entry, Frame, Label, Listbox, StringVar, Tk, filedialog, messagebox

from pypdf import PdfReader, PdfWriter


def parse_pages(spec: str, total: int) -> list[int]:
    if not spec.strip():
        return list(range(total))
    result: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            a, b = token.split("-", 1)
            start, end = int(a), int(b)
            if start > end:
                start, end = end, start
            result.extend(range(start - 1, end))
        else:
            result.append(int(token) - 1)
    dedup = []
    for idx in result:
        if idx < 0 or idx >= total:
            raise ValueError(f"Page out of range: {idx + 1}")
        if idx not in dedup:
            dedup.append(idx)
    return dedup


def strip_writer_metadata(writer: PdfWriter) -> None:
    writer.metadata = None
    writer.xmp_metadata = None
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)


def protect_writer(writer: PdfWriter, password: str) -> None:
    if password:
        writer.encrypt(password, algorithm="AES-256-R5")


def write_pdf(reader: PdfReader, pages: list[int], out: Path, remove_metadata: bool = True, password: str = "") -> None:
    writer = PdfWriter()
    for idx in pages:
        writer.add_page(reader.pages[idx])
    if remove_metadata:
        strip_writer_metadata(writer)
    protect_writer(writer, password)
    with out.open("wb") as fh:
        writer.write(fh)


def sanitize_pdf(src: Path, out: Path, page_spec: str = "", password: str = "") -> None:
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified by this MVP. Decrypt with authorization before processing.")
    pages = parse_pages(page_spec, len(reader.pages))
    write_pdf(reader, pages, out, remove_metadata=True, password=password)


def split_pdf(src: Path, output_dir: Path) -> int:
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified by this MVP.")
    output_dir.mkdir(parents=True, exist_ok=True)
    for i in range(len(reader.pages)):
        write_pdf(reader, [i], output_dir / f"{src.stem}_page_{i+1:03d}.pdf", remove_metadata=True)
    return len(reader.pages)


def merge_pdfs(inputs: list[Path], out: Path, password: str = "") -> None:
    writer = PdfWriter()
    for src in inputs:
        reader = PdfReader(str(src), strict=True)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF cannot be merged by this MVP: {src.name}")
        for page in reader.pages:
            writer.add_page(page)
    strip_writer_metadata(writer)
    protect_writer(writer, password)
    with out.open("wb") as fh:
        writer.write(fh)


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
        for p in filedialog.askopenfilenames(title="Select PDFs", filetypes=[("PDF", "*.pdf")]):
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
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"{self.files[0].stem}_clean.pdf", filetypes=[("PDF", "*.pdf")])
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
        folder = filedialog.askdirectory(title="Choose split output folder")
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
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="merged_clean.pdf", filetypes=[("PDF", "*.pdf")])
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

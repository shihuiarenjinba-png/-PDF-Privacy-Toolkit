from __future__ import annotations

from pathlib import Path
from tkinter import BOTH, END, LEFT, Button, Entry, Frame, Label, Listbox, StringVar, Tk, filedialog, messagebox
from tkinter import ttk
from pdf_export_review import review_pdf_inputs

from pypdf import PdfReader, PdfWriter


MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_INPUT_PAGES = 500
MAX_MERGE_FILES = 20


def check_pdf_input(path: Path) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError('Input must be a regular PDF file, not a symbolic link.')
    size = path.stat().st_size
    if size == 0 or size > MAX_INPUT_BYTES:
        raise ValueError('PDF input is empty or exceeds the 64 MiB limit.')


def check_page_count(reader: PdfReader) -> None:
    if not (1 <= len(reader.pages) <= MAX_INPUT_PAGES):
        raise ValueError('PDF exceeds the verified 1–500 page range.')


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
    check_pdf_input(src)
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified. Supply an authorized decrypted copy.")
    check_page_count(reader)
    pages = parse_pages(page_spec, len(reader.pages))
    write_pdf(reader, pages, out, remove_metadata=True, password=password)


def split_pdf(src: Path, output_dir: Path) -> int:
    check_pdf_input(src)
    reader = PdfReader(str(src), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDFs are not modified.")
    check_page_count(reader)
    count = len(reader.pages)
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
    if len(inputs) < 2 or len(inputs) > MAX_MERGE_FILES:
        raise ValueError("Select 2–20 PDFs to merge.")
    for src in inputs:
        ensure_distinct_path(src, out)
    if out.exists() or out.is_symlink():
        raise FileExistsError("Output PDF already exists. Choose a new filename.")
    writer = PdfWriter()
    total_pages = 0
    for src in inputs:
        check_pdf_input(src)
        reader = PdfReader(str(src), strict=True)
        check_page_count(reader)
        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF cannot be merged: {src.name}")
        if not reader.pages:
            raise ValueError(f"PDF has no pages: {src.name}")
        for page in reader.pages:
            writer.add_page(page)
            total_pages += 1
            if total_pages > MAX_INPUT_PAGES:
                raise ValueError('Merged PDF exceeds the verified 500-page limit.')
    strip_writer_metadata(writer)
    protect_writer(writer, password)
    _publish_writer(writer, out, total_pages, password)


class App:
    """One obvious workflow; advanced options stay hidden until needed."""

    def __init__(self, root: Tk):
        self.root = root
        self.root.title("PDF Privacy — Windows")
        self.root.geometry("930x650")
        self.root.minsize(820, 560)
        self.files: list[Path] = []
        self.pages = StringVar()
        self.password = StringVar()
        self.action = StringVar(value="Remove metadata / select pages")
        self.advanced_visible = False
        self.preview_revision: str | None = None

        head = Frame(root, padx=12, pady=12)
        head.pack(fill="x")
        Label(head, text="PDF Privacy", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        Label(head, text="Merge, split or remove document metadata. PDF page content is NOT redacted.",
              wraplength=840, justify=LEFT).pack(anchor="w")
        Label(head, text="① Add PDFs  →  ② Choose an action  →  ③ Preview  →  ④ Save a new PDF", font=("Segoe UI", 10, "bold"), wraplength=860, justify=LEFT).pack(anchor="w", pady=(4, 0))

        controls = Frame(root, padx=12)
        controls.pack(fill="x")
        Button(controls, text="1  Add PDF files", width=18, command=self.add_files).pack(side=LEFT)
        Label(controls, text="2  Action:").pack(side=LEFT, padx=(8, 2))
        ttk.Combobox(
            controls, state="readonly", width=24, textvariable=self.action,
            values=("Remove metadata / select pages", "Split first PDF", "Merge selected PDFs"),
        ).pack(side=LEFT, padx=8)
        Button(controls, text="3  Preview (no write)", width=23,
               command=self.preview_action).pack(side=LEFT, padx=(0, 6))
        Button(controls, text="4  Save new PDF", width=19,
               command=self.run_action).pack(side=LEFT)

        Button(root, text="Advanced: page order / password", command=self.toggle_advanced).pack(anchor="w", padx=12, pady=(8, 2))
        self.advanced = Frame(root, padx=12, pady=8)
        Label(self.advanced, text="Pages to keep / order (example 1,3-5,2; blank = all):").pack(anchor="w")
        Entry(self.advanced, textvariable=self.pages).pack(fill="x", pady=4)
        Label(self.advanced, text="Optional output password (AES-256-R5; not used for split):").pack(anchor="w")
        Entry(self.advanced, textvariable=self.password, show="*").pack(fill="x", pady=4)

        self.preview_status = StringVar(value="プレビュー後に新しいPDFを保存できます。")
        Label(root, textvariable=self.preview_status, wraplength=850,
              justify=LEFT).pack(anchor="w", padx=12, pady=(6, 4))
        Label(root, text="Input inspection (information only; embedded content is not fully checked):").pack(anchor="w", padx=12, pady=(10, 4))
        self.listbox = Listbox(root, font=("Consolas", 10))
        self.listbox.pack(fill=BOTH, expand=True, padx=12, pady=(0, 10))
        Label(root, text="Important: metadata removal does not remove visible text, attachments, form fields or annotations.",
              wraplength=850, justify=LEFT).pack(anchor="w", padx=12, pady=(0, 10))

    def toggle_advanced(self):
        self.advanced_visible = not self.advanced_visible
        if self.advanced_visible:
            self.advanced.pack(fill="x", before=self.listbox)
        else:
            self.advanced.pack_forget()

    def add_files(self):
        self.preview_revision = None
        for p in filedialog.askopenfilenames(parent=self.root, title="Select PDFs", filetypes=[("PDF", "*.pdf")]):
            path = Path(p)
            if path not in self.files:
                self.files.append(path)
        self.inspect_files()

    def inspect_files(self):
        self.listbox.delete(0, END)
        for p in self.files:
            try:
                check_pdf_input(p)
                reader = PdfReader(str(p), strict=True)
                check_page_count(reader)
                if reader.is_encrypted:
                    self.listbox.insert(END, f"[BLOCK] {p.name} | encrypted; no processing")
                    continue
                meta = bool(reader.metadata or reader.xmp_metadata)
                self.listbox.insert(
                    END, f"[REVIEW] {p.name} | {len(reader.pages)} pages | metadata flag={meta}"
                )
                self.listbox.insert(
                    END, "    Not inspected: embedded objects, attachments, image OCR, secrets"
                )
            except Exception as exc:
                self.listbox.insert(END, f"[BLOCK] {p.name}: {exc}")

    def preview_action(self):
        try:
            revision, detail = review_pdf_inputs(self.files, self.action.get(),
                                                 self.pages.get(), self.password.get(),
                                                 check_pdf_input=check_pdf_input,
                                                 check_page_count=check_page_count,
                                                 parse_pages=parse_pages)
            self.preview_revision = revision
            self.preview_status.set(detail + " 内容を確認してから保存してください。")
        except Exception as exc:
            self.preview_revision = None
            self.preview_status.set("プレビュー失敗。PDF・ページ指定・容量などを確認してください。")
            messagebox.showwarning("Preview failed", str(exc))

    def run_action(self):
        if not self.files:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add a PDF first.")
        try:
            revision, _ = review_pdf_inputs(self.files, self.action.get(),
                                             self.pages.get(), self.password.get(),
                                             check_pdf_input=check_pdf_input,
                                             check_page_count=check_page_count,
                                             parse_pages=parse_pages)
        except Exception as exc:
            self.preview_revision = None
            return messagebox.showerror("Preview required", str(exc))
        if not self.preview_revision or self.preview_revision != revision:
            self.preview_revision = None
            return messagebox.showwarning("Preview required",
                "Selected PDFs, operation or options changed. Preview the operation again.")
        action = self.action.get()
        # An approval can authorize exactly one user-requested operation.
        self.preview_revision = None
        if action == "Merge selected PDFs":
            return self.merge_all()
        if action == "Split first PDF":
            return self.split_first()
        return self.sanitize_first()

    def confirm_limited_scope(self) -> bool:
        return messagebox.askokcancel(
            "Check limitations before exporting",
            "Only PDF document-info / XMP metadata is targeted for removal.\n"
            "Visible text, hidden objects, signatures, forms, annotations and attachments "
            "are not securely redacted. Pages are not independently rendered.\n"
            "Processing may change PDF structure and signatures. Verify the exported file.\nContinue?",
        )

    def sanitize_first(self):
        if not self.files:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add a PDF first.")
        if not self.confirm_limited_scope():
            return
        out = filedialog.asksaveasfilename(
            parent=self.root, defaultextension=".pdf",
            initialfile=f"{self.files[0].stem}_metadata_removed.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        try:
            sanitize_pdf(self.files[0], Path(out), self.pages.get(), self.password.get())
            messagebox.showinfo("PDF Privacy Toolkit", f"Created and verified metadata/page count: {out}\nReview content before sharing.")
        except Exception as exc:
            messagebox.showerror("PDF Privacy Toolkit", str(exc))

    def split_first(self):
        if not self.files:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add a PDF first.")
        if not self.confirm_limited_scope():
            return
        folder = filedialog.askdirectory(parent=self.root, title="Choose split output folder")
        if not folder:
            return
        try:
            count = split_pdf(self.files[0], Path(folder))
            messagebox.showinfo("PDF Privacy Toolkit", f"Created and verified {count} one-page PDFs. Review content before sharing.")
        except Exception as exc:
            messagebox.showerror("PDF Privacy Toolkit", str(exc))

    def merge_all(self):
        if len(self.files) < 2:
            return messagebox.showinfo("PDF Privacy Toolkit", "Add at least two PDFs to merge.")
        if not self.confirm_limited_scope():
            return
        out = filedialog.asksaveasfilename(
            parent=self.root, defaultextension=".pdf",
            initialfile="merged_metadata_removed.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return
        try:
            merge_pdfs(self.files, Path(out), self.password.get())
            messagebox.showinfo("PDF Privacy Toolkit", f"Created and verified merged PDF: {out}\nReview content before sharing.")
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

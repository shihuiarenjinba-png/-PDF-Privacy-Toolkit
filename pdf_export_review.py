"""Read-only PDF operation approval for the beginner desktop UI."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def review_pdf_inputs(files: list[Path], action: str, pages: str, password: str) -> tuple[str, str]:
    from pypdf import PdfReader
    from windows_app import check_pdf_input, check_page_count, parse_pages

    if not files:
        raise ValueError("先にPDFを選択してください。")
    if action not in {"Remove metadata / select pages", "Split first PDF", "Merge selected PDFs"}:
        raise ValueError("未対応の処理方法です。")
    if action == "Merge selected PDFs" and len(files) < 2:
        raise ValueError("PDFの結合には2件以上のファイルが必要です。")
    selected = files if action == "Merge selected PDFs" else files[:1]
    revisions = []
    counts = []
    for path in selected:
        if path.is_symlink():
            raise ValueError("シンボリックリンクのPDFは指定できません。")
        check_pdf_input(path)
        with path.open("rb") as fh:
            digest = hashlib.sha256()
            for block in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(block)
        reader = PdfReader(str(path), strict=True)
        if reader.is_encrypted:
            raise ValueError(f"{path.name}: 暗号化入力PDFは処理できません。")
        check_page_count(reader)
        revisions.append((str(path.resolve()), digest.hexdigest()))
        counts.append(len(reader.pages))
    if action == "Remove metadata / select pages" and pages.strip():
        selected_pages = parse_pages(pages, counts[0])
        out_count = len(selected_pages)
    elif action == "Split first PDF":
        out_count = counts[0]
    else:
        out_count = sum(counts) if action == "Merge selected PDFs" else counts[0]
    settings = {"action": action, "pages": pages, "password": password,
                "files": revisions}
    revision = hashlib.sha256(json.dumps(settings, ensure_ascii=False,
                                       sort_keys=True).encode("utf-8")).hexdigest()
    label = (f"{len(selected)}件のPDF（合計{sum(counts)}ページ）を検査しました。"
             f"出力予定: {out_count}ページ/ファイル。"
             "本文・注釈・添付・フォームは機密除去の保証対象外です。")
    return revision, label

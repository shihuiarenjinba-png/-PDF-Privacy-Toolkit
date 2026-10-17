# PDF Privacy Toolkit — Simple Windows MVP (not a redaction product)

## Only three everyday actions
1. Choose one or more PDFs.
2. Choose **Remove metadata / select pages**, **Split first PDF**, or **Merge selected PDFs**.
3. Export a **new** output; advanced page ordering and AES-256-R5 password settings are collapsed by default.

**Important distinction:** removing document-info/XMP metadata is not removing personally identifying PDF page content. This product does not currently implement certified redaction, OCR, embedded-file removal, form-field erasure, annotations cleanup or complete hidden-object analysis. Do not call its output "fully sanitized."

## Safety controls in this improvement branch
- Strict one-based page parser; missing/invalid/zero/out-of-range/empty page specs rejected; preserve order while removing duplicate page requests.
- Malformed and encrypted inputs are not automatically modified.
- Reject outputs that collide with input PDFs or any other existing file. Exclusive file creation prevents overwrite even if a target appears after the GUI check.
- Reopen each new PDF to validate strict parse, expected page count, expected encryption status and absence of document-info/XMP fields.
- Split checks that *all* targets are absent before writing. If an individual split fails, its newly written sibling outputs are removed. Existing user files remain untouched.
- User confirmation explains limited privacy scope and that structure, digital signatures, visible content, forms and attachments might survive or be changed.
- The current implementation has no external upload feature.

## Existing separate form workflow
The repository's `main` contains `batch_form_filler.py`, `batch_form_gui.py`, Windows QA utilities and a separate form-processing product line. **This work is based on `windows-mvp-20260915` and deliberately does not modify those main files.** Form automation and page/metadata operations require separate product/launcher decisions; no code is auto-merged across these branches.

## Source tests (Windows/Python)
```powershell
py -3 -m pip install --requirement requirements-windows.lock.txt
py -3 -m compileall -q windows_app.py i18n.py tests
py -3 .\smoke_test.py
py -3 -m unittest discover -s tests -p 'test_*.py' -v
py -3 .\bilingual_smoke_test.py
py -3 .\dialog_parent_smoke_test.py
```

Portable development EXE builder: `build-windows-portable.ps1`. A portable EXE is **not** a Store MSIX. Do not upload it as a Store package.

## Sales gate: HOLD
Need executed test results (CI or equivalent), real Windows 10/11 GUI and DPI acceptance, large/hostile PDF corpus, signatures/forms/annotations/rendering behavior, post-process deep object checks if redaction is ever added, network/egress test, third-party license audit, product artwork, real Partner Center identity, official MSIX build and install/update/uninstall, Store certification, privacy policy, screenshots, listing and justified pricing. Product must not claim complete confidentiality protection.

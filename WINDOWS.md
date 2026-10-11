# PDF Privacy Toolkit — Windows MVP

## Implemented

- Merge multiple PDFs
- Split a PDF into one-page files
- Keep/delete/reorder pages using a page specification such as `1,3-5,2`
- Remove PDF metadata on generated outputs
- Optional password encryption

All operations are local and use pypdf.

## Run

```powershell
py -3 -m pip install pypdf
py -3 .\windows_app.py
```

## Build

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-portable.ps1
```

Output: `dist\PDFPrivacyToolkit.exe`

## Sales note

Raster flattening/redaction is not claimed in this MVP because reliable visual redaction requires rendering and verification. Before sale test encrypted PDFs, malformed PDFs, page ordering, metadata removal, Windows 10/11, malware scan, Authenticode signing and SHA256.

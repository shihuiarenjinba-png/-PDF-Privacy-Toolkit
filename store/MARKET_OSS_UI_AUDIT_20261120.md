# Market / OSS reference audit — 2026-11-20

Product: **PDF Privacy** (Group C Store candidate branch)

## References reviewed
- Dangerzone: rebuilds untrusted documents through a constrained conversion pipeline and treats metadata destruction as a distinct security goal.
  - https://github.com/freedomofpress/dangerzone
- Stirling PDF: local/self-hostable PDF tooling with separate edit, redact, merge, split, OCR and metadata-related operations.
  - https://github.com/Stirling-Tools/Stirling-PDF

## Decisions for this product
- Keep structural privacy operations explicit: metadata removal, annotations/forms/actions inspection, page operations and redaction must not collapse into one vague “safe” result.
- Visual black boxes alone are not equivalent to true content removal.
- Preserve new-file output and post-export verification where supported.
- Strong flatten/rebuild behavior, when offered, must be clearly labelled as a stronger/destructive compatibility trade-off.
- Do not reuse PDFBatchForms/main-branch CI as proof that this Group C Store candidate passed release QA.
- Treat this document as design evidence only; no third-party code was copied.

## Remaining release evidence
- Real Windows tests for metadata, annotations/forms, page operations, password output and redaction/verification fixtures supported by this branch.
- DPI/visual QA, exact Store version/assets, QA_UNSIGNED MSIX and manifest/hash evidence.

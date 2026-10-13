# Windows 10/11 manual acceptance checklist (OPEN)

**Status: NOT EXECUTED. Not a sales release approval.**

## Safe setup

Run only with disposable synthetic data, never on the only copy of work files. Use a normal Windows user account (avoid running as Administrator). Clone the repository, open PowerShell from the repository folder, then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-validation.ps1
```

Find the generated executable under `dist-validation\<Product>-<GUID>\<Product>\<Product>.exe`. The script produces an unsigned **validation** build, not a store package. If GitHub Actions shows Success, that does NOT mean human GUI operation has been tested.

## Human test scenarios

1. [ ] Use a locally generated *text-AcroForm* PDF and 2-row CSV; visually inspect both resulting PDFs in Microsoft Edge and Adobe Acrobat Reader.
2. [ ] Verify every field, page, filename and count; compare the original PDF and CSV hashes before/after.
3. [ ] Test Japanese names, addresses and symbols; inspect displayed glyphs and printed/previewed text (automated field-value equality alone is insufficient).
4. [ ] Attempt unsupported signed/XFA/encrypted PDFs, checkboxes and unknown field mappings; require an explicit rejection.
5. [ ] Inspect output PDF annotations, metadata, embedded files and actions; never treat form-filling as a privacy sanitization function.
## Evidence required before approval

- Record Windows edition/build (10 or 11), language, screen scaling, user mode, EXE path and SHA-256.
- Record pass/fail and sanitized screenshot for each manual case; ensure no personal/customer information is visible.
- Save before/after hashes of source test files and attach synthetic input, output and report examples to the local QA record.
- Check Defender/security scan output and packaging dependencies; validate offline operation and absence of unexpected network calls.
- Test exit, relaunch and cleanup; do not claim installer/MSIX/uninstall success before separately testing them.
- Verify both Windows 10 and 11 (or explicitly record whichever is unavailable).
- Any crash, data overwrite, false clean result, unsigned binary reputation warning, unreadable Japanese PDF glyph or unreviewed security concern blocks release.

**Gate:** `MANUAL_WINDOWS_ACCEPTANCE_PENDING` / `RELEASE_BLOCKED`. Never promote to sales approval based only on CI-generated EXE and automated GUI fixtures.

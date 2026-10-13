# Windows validation record — 2026-10-13

## Confirmed CI result

- Repository: `-PDF-Privacy-Toolkit`
- Test-only branch: `validation/windows-20261013`
- Tested commit: `5fcf6285f8ec9cb27ab5ded59fd1776b8e0e3a46`
- Windows GitHub Actions run: https://github.com/shihuiarenjinba-png/-PDF-Privacy-Toolkit/actions/runs/38386274692
- Runner environment: `windows-latest`, Python 3.11
- Automated unit tests run: **4, passing**
- PyInstaller Windows one-directory executable: **built successfully**
- Generated executable name: `PDFBatchForms.exe`
- EXE SHA-256 (ephemeral CI build): `612021058AB6AB70B99E824737DDD459E5A9D3BCBB538DE4B4E4F46EB4998C8A`
- Workflow conclusion: **success**

## Restrictions / release gates

- **NOT A SALES RELEASE.** EXE is unsigned and no manual GUI/window interaction tests were run.
- GitHub Actions artifact quota was exceeded. Binary upload was disabled; no downloadable build is preserved by this run. SHA-256 alone is not an EXE download.
- Windows host integration and actual GUI interactions, malware/Defender checks, signing, installer/MSIX, privacy review and Microsoft Store certification remain pending.
- Current automated tests are focused regression fixtures; they do not certify every file format, filesystem edge case, encoding, performance, security behavior, or real user dataset.
- `main` retains manually triggered `windows-validation.yml`; the push trigger exists only on the isolated validation branch.
- A future build from the same sources might not reproduce this hash unless the toolchain and dependencies are pinned.
- Do not merge the validation-only push trigger or claim full release approval.

## Next steps

1. Run the existing PowerShell validation script on a controlled Windows 10/11 test PC.
2. Perform explicit GUI open/import/output/safety tests, including negative and non-ASCII cases.
3. Audit compiled binaries, dependencies, egress, filesystem writes, uninstall, Defender results.
4. Sign release candidates and inspect manifest/AV results before creating an MSIX or selling.

Status: `AUTOMATED_WINDOWS_TEST_AND_BUILD_PASS / RELEASE_BLOCKED`.

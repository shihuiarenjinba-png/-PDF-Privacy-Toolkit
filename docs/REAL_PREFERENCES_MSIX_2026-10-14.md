# Real GUI preferences and installed MSIX update — 2026-10-14

- **Product:** PDFBatchForms (existing repository `-PDF-Privacy-Toolkit`)
- **Windows CI evidence:** https://github.com/shihuiarenjinba-png/-PDF-Privacy-Toolkit/actions/runs/38477467465 — SUCCESS
- **Regression tests:** 8 passing
- **Saved real GUI settings:** PDF帳票出力フォルダ（output）

A button labeled **設定を保存** writes a versioned UTF-8 JSON preferences file to the per-user local storage area. On the next app launch the GUI restores the stored settings. The application stores only allowlisted preferences, **never source/business file contents**. Save writes through a temporary file with fsync and atomic replace. Damaged or future-version data is NOT overwritten without notice.

When packaged: `%LOCALAPPDATA%\Packages\<ActualPackageFamilyName>\LocalState\PDFBatchForms\preferences.json`. When unpackaged: `%LOCALAPPDATA%\PDFBatchForms\preferences.json`.

**CI-proven behavior:** The installed synthetic MSIX application at 1.0.0.0 used its real GUI **設定を保存** button with representative, synthetic Japanese-text and numeric settings. Following a same-family upgrade to 1.0.1.0, the original JSON passed SHA-256 preservation and a fresh packaged GUI startup reloaded the correct settings. Ephemeral test package and certificate removed after success.

**Remaining limitations:** Prior released-version preferences and any future schema migrations are NOT tested; business report files are NOT moved into app state; PDF glyph rendering, human clicks, local Windows 10/11 devices, real customer datasets, Defender/security certification, production Store identity and licensing remain UNVERIFIED. MSIX uninstall may remove the app's LocalState; update retention does not mean uninstall retention.

**Status: REAL_GUI_SETTINGS_SURVIVE_MSIX_UPDATE_CI_PASS / RELEASE_BLOCKED.**

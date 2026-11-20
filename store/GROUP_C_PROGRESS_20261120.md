# Group C progress evidence — 2026-11-20

Product: **PDF Privacy** (Group C Store candidate branch)

## Validated source before this record
- Source HEAD: `b2123fb52397d2c053f51d90c9fdf82631c541c6`
- GitHub Actions run: `44685188297`
- build-portable: **SUCCESS**
- regression suite: **SUCCESS**
- packaged EXE self-test: **PASS**
- package-unsigned-msix: **SUCCESS**
- real Store candidate build: **SKIPPED by approval gate**

## QA-only package evidence
- Portable EXE SHA-256: `1E7F6D1EF3CE60BBA5C60416574B6E4A493A3244015C80192F9155E60A651872`
- QA version: `1.0.52.0` — workflow-generated, **NOT an approved Store version**
- Package: `PDFPrivacyToolkit_QA_UNSIGNED_1.0.52.0_x64.msix`
- MSIX SHA-256: `B9AD559B7CA0E356C270F853E2D74332C2A0C92F9176D0C8AC485CE4EDD5D38C`
- Manifest identity check: **PASS**
- Artifact ID: `14606296524`
- Sales release: `HOLD`

## Current blockers for a real Store candidate
- package version approval is not OWNER_APPROVED
- brand assets approval is not OWNER_APPROVED
- approved Store version is missing
- approved asset directory and `store-assets/approval.json` are missing
- real supported PDF fixture review and Windows human DPI/visual acceptance remain separate
- PDFBatchForms/main-branch evidence must not be substituted for this branch

Do not upload the QA_UNSIGNED package as a production Store package.

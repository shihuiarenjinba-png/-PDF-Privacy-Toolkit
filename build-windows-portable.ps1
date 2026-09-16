$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw "Python launcher 'py' is required." }
$Venv = Join-Path $Root ".venv-build"
if (Test-Path $Venv) { Remove-Item -Recurse -Force $Venv }
py -3 -m venv $Venv
$Python = Join-Path $Venv "Scripts\python.exe"
& $Python -m pip install --upgrade pip
& $Python -m pip install pyinstaller "pypdf[crypto]>=6.0,<7"
& $Python -m PyInstaller --noconfirm --clean --onefile --windowed --name "PDFPrivacyToolkit" --collect-all pypdf --collect-all cryptography desktop_entry.py
Write-Host "Built: $Root\dist\PDFPrivacyToolkit.exe"
Write-Host "Before sale: run SALES_RELEASE_CHECKLIST.md, fixture tests, malformed/encrypted PDF tests, metadata/XMP verification, AES-256-R5 password test, JA/EN UI smoke, malware scan, Authenticode signing, SHA256."

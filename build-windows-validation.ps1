# Validation packaging only. NOT signed / NOT a sales release.
# Run in PowerShell from any location: powershell -ExecutionPolicy Bypass -File .\build-windows-validation.ps1
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
$root = $PSScriptRoot
Set-Location $root
$stamp = [Guid]::NewGuid().ToString("N")
$venv = Join-Path $env:TEMP ("PDFBatchForms-validation-" + $stamp)
$python = Join-Path $venv "Scripts\python.exe"
$out = Join-Path $root ("dist-validation\PDFBatchForms-" + $stamp)
$work = Join-Path $venv "pyinstaller-work"
$spec = Join-Path $venv "pyinstaller-spec"

function Assert-Code {
    if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" }
}
function Invoke-Python([string[]]$Options) {
    & $python @Options
    Assert-Code
}
try {
    py -3 -m venv $venv
    Assert-Code
    Invoke-Python @("-m","pip","install","--upgrade","pip")
    Invoke-Python @("-m","pip","install","-r","requirements-batch-form.txt")
    Invoke-Python @("-m","pip","install","reportlab>=4,<5")
    Invoke-Python @("-m","pip","install","pyinstaller>=6.10,<7")
    Invoke-Python @("-m","unittest","discover","-s","tests","-p","test_batch_form_filler.py","-v")
    Invoke-Python @("-m","PyInstaller","--noconfirm","--clean","--onedir","--windowed",
        "--name","PDFBatchForms","--distpath",$out,"--workpath",$work,"--specpath",$spec,
        "batch_form_gui.py")
    $exe = Join-Path $out "PDFBatchForms\PDFBatchForms.exe"
    if (-not (Test-Path -LiteralPath $exe)) { throw "Expected EXE missing: $exe" }
    $digest = Get-FileHash -Algorithm SHA256 -LiteralPath $exe
    $result = [ordered]@{
        product = "PDFBatchForms"
        validation_only = $true
        sales_release = $false
        signed = $false
        exe = $exe
        sha256 = $digest.Hash
        created_utc = (Get-Date).ToUniversalTime().ToString("o")
        windows_gui_runtime_tested = $false
        microsoft_defender_checked = $false
    }
    $result | ConvertTo-Json -Depth 3 | Set-Content -Encoding UTF8 (Join-Path $out "validation-manifest.json")
    Write-Host "VALIDATION BUILD CREATED: $exe"
    Write-Host "SHA256: $($digest.Hash)"
    Write-Host "Not signed. GUI not smoke tested. NOT FOR SALE."
} finally {
    if (Test-Path -LiteralPath $venv) { Remove-Item -LiteralPath $venv -Recurse -Force }
}

# WSNRUN.ps1
# Runs all WSN-CA feature files and generates a combined QA execution dashboard.
#
# Usage:
#   .\WSNRUN.ps1              # dev environment (default)
#   .\WSNRUN.ps1 -Env prod    # production environment

param(
    [ValidateSet("prod", "dev")]
    [string]$Env = "dev"
)

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force

# Prefer .venv, fall back to env/, then PATH.
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    & ".\.venv\Scripts\Activate.ps1"
    $python = ".\.venv\Scripts\python.exe"
} elseif (Test-Path ".\env\Scripts\Activate.ps1") {
    & ".\env\Scripts\Activate.ps1"
    $python = ".\env\Scripts\python.exe"
} else {
    $python = "python"
}
Write-Host "Using Python: $python"

# Force UTF-8 for Python I/O so behave_html_formatter doesn't truncate on
# non-cp1252 characters captured from the application.
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ErrorActionPreference = "Continue"

# ── Prepare output directories ────────────────────────────────────────────────
$jsonReportDir = "reports/json-report"
New-Item -ItemType Directory -Path $jsonReportDir -Force | Out-Null
Get-ChildItem -Path $jsonReportDir -Filter "*.json" -ErrorAction SilentlyContinue | Remove-Item -Force

$htmlFeatureDir = "reports/html-report/features"
New-Item -ItemType Directory -Path $htmlFeatureDir -Force | Out-Null
Get-ChildItem -Path $htmlFeatureDir -Filter "*.html" -ErrorAction SilentlyContinue | Remove-Item -Force

New-Item -ItemType Directory -Path "reports/allure-results" -Force | Out-Null

# ── Single run — all features in one behave invocation ───────────────────────
$env:USER_TYPE = $Env   # "dev" or "prod" — config.py reads this
$jsonOut = Join-Path $jsonReportDir "all.json"
$htmlOut = Join-Path $htmlFeatureDir "all.html"

Write-Host "`n► Running all features at once  (USER_TYPE=$($env:USER_TYPE))"
& $python -m behave features/ `
    -f allure_behave.formatter:AllureFormatter -o reports/allure-results `
    -f json.pretty                             -o $jsonOut `
    -f behave_html_formatter:HTMLFormatter     -o $htmlOut `
    --no-capture

$runFailed = ($LASTEXITCODE -ne 0)
if ($runFailed) { Write-Warning "One or more scenarios failed." }

# ── Combined HTML dashboard ───────────────────────────────────────────────────
Write-Host "`nGenerating combined QA dashboard..."
& $python scripts/combine_feature_reports.py `
    $jsonOut `
    $htmlOut `
    "reports/html-report/combined_report.html" `
    $Env

$reportExitCode = $LASTEXITCODE

if ($reportExitCode -ne 0) {
    Write-Host "`nRun completed, but combined HTML report generation failed."
    exit $reportExitCode
} elseif ($runFailed) {
    Write-Host "`nOne or more scenarios had failures."
    Write-Host "Combined report saved to: reports/html-report/"
    exit 1
} else {
    Write-Host "`nAll scenarios passed."
    Write-Host "Combined report saved to: reports/html-report/"
    exit 0
}

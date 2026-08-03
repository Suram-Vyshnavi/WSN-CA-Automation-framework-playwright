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
# Old report files are removed (not just left for behave to overwrite) because a
# leftover file from a prior run that's still mid-release by the OS (transient
# lock right after that process exits) can cause behave to write into a
# non-empty file instead of a fresh one - corrupting all.json with old+new JSON
# concatenated, which then silently breaks the combined dashboard's metrics.
# Retry on a lock instead of silently giving up (previous behavior swallowed
# the failure via -ErrorAction SilentlyContinue and let that corruption happen).
function Remove-ReportFilesWithRetry([string]$Dir, [string]$Filter) {
    $files = Get-ChildItem -Path $Dir -Filter $Filter -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $attempts = 0
        while ($attempts -lt 10) {
            try {
                Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                break
            } catch {
                $attempts++
                if ($attempts -ge 10) {
                    throw "Could not remove stale report file '$($file.FullName)' - it is still locked by another process (e.g. a previous run still shutting down). Close whatever holds it open and re-run. $_"
                }
                Start-Sleep -Milliseconds 500
            }
        }
    }
}

$jsonReportDir = "reports/json-report"
New-Item -ItemType Directory -Path $jsonReportDir -Force | Out-Null
Remove-ReportFilesWithRetry -Dir $jsonReportDir -Filter "*.json"

$htmlFeatureDir = "reports/html-report/features"
New-Item -ItemType Directory -Path $htmlFeatureDir -Force | Out-Null
Remove-ReportFilesWithRetry -Dir $htmlFeatureDir -Filter "*.html"

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

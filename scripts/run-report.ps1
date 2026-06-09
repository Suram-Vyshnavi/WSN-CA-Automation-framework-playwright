# Runs the homepage feature and generates both Allure and the Wadhwani Foundation
# themed HTML report.
#
# Usage:  ./scripts/run-report.ps1
#         ./scripts/run-report.ps1 features/homepage.feature

param(
    [string]$Feature = "features/homepage.feature"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

# Prefer the .venv interpreter; fall back to env, then PATH.
if (Test-Path ".\.venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} elseif (Test-Path ".\env\Scripts\python.exe") {
    $python = ".\env\Scripts\python.exe"
} else {
    $python = "python"
}

& $python -m behave $Feature `
    -f allure_behave.formatter:AllureFormatter -o reports/allure-results `
    -f utils.wf_html_formatter:WFHTMLFormatter -o reports/html-report/report.html `
    --no-capture

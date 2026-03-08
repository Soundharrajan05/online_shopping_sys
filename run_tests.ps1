# PowerShell script to run tests with proper environment setup
# This sets the DB_PASSWORD and runs pytest

param(
    [string]$TestPath = "tests/",
    [switch]$Verbose,
    [switch]$Coverage
)

Write-Host "=== Running Tests ===" -ForegroundColor Cyan
Write-Host ""

# Set environment variable for database password
$env:DB_PASSWORD = 'Soundhar@54321'

# Build pytest command
$pytestArgs = @($TestPath)

if ($Verbose) {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += "--cov=app"
    $pytestArgs += "--cov-report=html"
}

Write-Host "Running: pytest $($pytestArgs -join ' ')" -ForegroundColor Yellow
Write-Host ""

# Run pytest
& pytest @pytestArgs

Write-Host ""
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
}

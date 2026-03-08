# PowerShell script to setup MySQL test database
# This script creates the test database and loads the schema

Write-Host "=== MySQL Test Database Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if MySQL is accessible
Write-Host "Checking MySQL installation..." -ForegroundColor Yellow
try {
    $mysqlVersion = & mysql --version 2>&1
    Write-Host "✓ MySQL found: $mysqlVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ MySQL not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure MySQL is installed and added to PATH" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Create 'shopping_system_test' database" -ForegroundColor White
Write-Host "  2. Load the database schema" -ForegroundColor White
Write-Host "  3. Verify the setup" -ForegroundColor White
Write-Host ""

# Prompt for MySQL root password
$password = Read-Host "Enter MySQL root password (press Enter if no password)" -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

Write-Host ""
Write-Host "Setting up test database..." -ForegroundColor Yellow

# Run the setup script
if ($plainPassword -eq "") {
    # No password
    $result = & mysql -u root < setup_test_db.sql 2>&1
} else {
    # With password
    $result = & mysql -u root "-p$plainPassword" < setup_test_db.sql 2>&1
}

# Check if successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Test database setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Set the DB_PASSWORD environment variable:" -ForegroundColor White
    if ($plainPassword -eq "") {
        Write-Host "     `$env:DB_PASSWORD = ''" -ForegroundColor Gray
    } else {
        Write-Host "     `$env:DB_PASSWORD = 'your_password'" -ForegroundColor Gray
    }
    Write-Host "  2. Run the property tests:" -ForegroundColor White
    Write-Host "     pytest tests/test_auth_properties.py -v" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✗ Error setting up database:" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  - Incorrect password" -ForegroundColor White
    Write-Host "  - MySQL server not running" -ForegroundColor White
    Write-Host "  - Insufficient permissions" -ForegroundColor White
    exit 1
}

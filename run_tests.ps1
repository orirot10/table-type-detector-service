Write-Host "Activating virtual environment if exists..."

# Activate venv
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
}

Write-Host "Running style checks (flake8 if installed)..."
if (Get-Command flake8 -ErrorAction SilentlyContinue) {
    flake8 app tests
} else {
    Write-Host "flake8 not installed - skipping style check"
}

Write-Host "Running pytest..."
$env:PYTHONPATH = "."
pytest --maxfail=1 --disable-warnings -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "All tests passed successfully."
} else {
    Write-Host "Some tests failed."
}

exit $LASTEXITCODE

Write-Host "Checking virtual environment..."

# Create venv if not exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies if needed
Write-Host "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Set default .env if missing
if (-not (Test-Path ".env")) {
    Write-Host "Creating default .env file..."
    @"
MODEL_PATH=./model/table_type_identification.pt
TABLE_LABELS=balance activity
# API_KEY=your_api_key_here
"@ | Out-File ".env" -Encoding UTF8
    Write-Host ".env file created. You may update it if needed."
}

# Run API locally
Write-Host "Starting FastAPI server..."
python -m uvicorn app.main:app --reload --port 8000

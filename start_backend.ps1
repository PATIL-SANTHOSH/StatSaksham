# Start StatSaksham FastAPI Backend Server
Write-Host "Starting StatSaksham FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

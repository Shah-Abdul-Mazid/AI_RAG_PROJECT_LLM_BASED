# Enterprise AI Runner Script

Write-Host "Starting Antigravity Enterprise AI..." -ForegroundColor Cyan

# Check for .env in backend
if (!(Test-Path "backend/.env")) {
    Write-Host "Warning: backend/.env not found. Please create it with your GOOGLE_API_KEY." -ForegroundColor Yellow
}

# Start Backend
Write-Host "Launching Backend (FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python main.py"

# Start Frontend
Write-Host "Launching Frontend (Next.js)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "System is starting up!" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"

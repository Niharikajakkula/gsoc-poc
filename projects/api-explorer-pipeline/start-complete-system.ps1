Write-Host "🚀 Starting API Explorer Complete System" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $pythonVersion = python --version
    Write-Host "✅ Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python from https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Starting backend server on port 3002..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; Write-Host '🚀 Backend Server Starting...' -ForegroundColor Green; node simple-server.js"

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "🌐 Starting frontend server on port 8000..." -ForegroundColor Yellow
Set-Location ..
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host '🌐 Frontend Server Starting...' -ForegroundColor Green; python start-frontend-server.py"

Write-Host ""
Write-Host "✅ System startup complete!" -ForegroundColor Green
Write-Host "🔗 Backend: http://localhost:3002" -ForegroundColor Cyan
Write-Host "🌐 Frontend: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Note: Two new PowerShell windows should have opened." -ForegroundColor Yellow
Write-Host "   - One for the backend server (port 3002)" -ForegroundColor Yellow
Write-Host "   - One for the frontend server (port 8000)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🛑 To stop: Close both PowerShell windows or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this setup script..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
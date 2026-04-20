Write-Host "Starting API Explorer Backend..." -ForegroundColor Green
Set-Location backend
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host "Node.js version:" -ForegroundColor Yellow
node --version
Write-Host ""
Write-Host "Starting server on port 3002..." -ForegroundColor Green
Write-Host "Backend URL: http://localhost:3002" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
node simple-server.js
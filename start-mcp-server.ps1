# Start MCP Server Script
# Starts the API Explorer MCP server for AI agent integration

Write-Host "🚀 Starting API Explorer MCP Server" -ForegroundColor Cyan
Write-Host "=" * 40

# Check if backend is running
Write-Host "Checking backend connection..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3002/" -Method GET -ErrorAction Stop
    Write-Host "✅ Backend is running: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not running. Starting backend first..." -ForegroundColor Red
    Write-Host "Please run: cd backend && node simple-server.js" -ForegroundColor White
    Write-Host "Then restart this script." -ForegroundColor White
    exit 1
}

# Navigate to MCP server directory
if (Test-Path "mcp-server") {
    Set-Location "mcp-server"
    
    # Check if dependencies are installed
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing MCP server dependencies..." -ForegroundColor Yellow
        npm install
    }
    
    Write-Host "Starting MCP server..." -ForegroundColor Green
    Write-Host "Available tools: search_apis, list_apis, execute_api" -ForegroundColor Gray
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    
    # Start the MCP server
    npm start
} else {
    Write-Host "❌ MCP server directory not found!" -ForegroundColor Red
    Write-Host "Make sure you're in the project root directory." -ForegroundColor White
}
# Start Frontend Server for API Explorer
# This serves the frontend on http://localhost:3001 to avoid CORS issues

Write-Host "🚀 Starting API Explorer Frontend Server..." -ForegroundColor Green

# Check if Python is available
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "📡 Using Python HTTP server on port 3001" -ForegroundColor Yellow
    Write-Host "🌐 Frontend will be available at: http://localhost:3001" -ForegroundColor Cyan
    Write-Host "📝 Make sure backend is running on port 3002" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Change to frontend directory and start server
    Set-Location frontend
    python -m http.server 3001
} elseif (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "📡 Using Node.js HTTP server on port 3001" -ForegroundColor Yellow
    Write-Host "🌐 Frontend will be available at: http://localhost:3001" -ForegroundColor Cyan
    Write-Host "📝 Make sure backend is running on port 3002" -ForegroundColor Yellow
    Write-Host ""
    
    # Create a simple Node.js server
    $serverScript = @"
const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
    let filePath = '.' + req.url;
    if (filePath === './') filePath = './index.html';
    
    const extname = String(path.extname(filePath)).toLowerCase();
    const mimeTypes = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.woff': 'application/font-woff',
        '.ttf': 'application/font-ttf',
        '.eot': 'application/vnd.ms-fontobject',
        '.otf': 'application/font-otf',
        '.wasm': 'application/wasm'
    };

    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if(error.code == 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 Not Found</h1>', 'utf-8');
            } else {
                res.writeHead(500);
                res.end('Server Error: ' + error.code + ' ..\n');
            }
        } else {
            res.writeHead(200, { 
                'Content-Type': contentType,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(3001, () => {
    console.log('🚀 Frontend server running at http://localhost:3001');
});
"@
    
    Set-Location frontend
    $serverScript | Out-File -FilePath "temp-server.js" -Encoding UTF8
    node temp-server.js
} else {
    Write-Host "❌ Neither Python nor Node.js found!" -ForegroundColor Red
    Write-Host "Please install Python or Node.js to run the frontend server" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Open frontend/index.html directly in browser" -ForegroundColor Gray
    Write-Host "(Note: This may cause CORS issues with the backend)" -ForegroundColor Gray
}
# PowerShell wrapper for mcp-gh-project MCP server
# Loads GitHub PAT from .env.github and launches Python MCP server

$ErrorActionPreference = "Stop"

# Path to .env.github file
$EnvFile = Join-Path $PSScriptRoot "../../.env.github"

# Check if .env.github exists
if (-not (Test-Path $EnvFile)) {
    Write-Error ".env.github not found at $EnvFile"
    exit 1
}

# Parse .env.github and load environment variables
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^GITHUB_PERSONAL_ACCESS_TOKEN=(.+)$') {
        $env:GITHUB_PERSONAL_ACCESS_TOKEN = $Matches[1]
        Write-Host "Loaded GITHUB_PERSONAL_ACCESS_TOKEN from .env.github" -ForegroundColor Green
    }
    if ($_ -match '^GITHUB_PERSONAL_USER_NAME=(.+)$') {
        $env:GITHUB_PERSONAL_USER_NAME = $Matches[1]
        Write-Host "Loaded GITHUB_PERSONAL_USER_NAME from .env.github" -ForegroundColor Green
    }
}

# Validate token was loaded
if (-not $env:GITHUB_PERSONAL_ACCESS_TOKEN) {
    Write-Error "GITHUB_PERSONAL_ACCESS_TOKEN not found in .env.github"
    exit 1
}

# Get Python executable path
$PythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PythonPath) {
    Write-Error "Python not found in PATH"
    exit 1
}

# Get path to server.py
$ServerPath = Join-Path $PSScriptRoot "../src/server.py"
if (-not (Test-Path $ServerPath)) {
    Write-Error "server.py not found at $ServerPath"
    exit 1
}

Write-Host "Starting mcp-gh-project MCP server..." -ForegroundColor Cyan
Write-Host "Python: $PythonPath" -ForegroundColor Gray
Write-Host "Server: $ServerPath" -ForegroundColor Gray

# Launch Python MCP server with environment variables
& $PythonPath $ServerPath

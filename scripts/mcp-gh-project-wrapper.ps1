# PowerShell wrapper for mcp-gh-project MCP server
# Loads GitHub PAT from .env.github and launches Python MCP server

$ErrorActionPreference = "Stop"

# Path to .env.github file (3 levels up: scripts -> mcp-gh-project -> _ -> .miast0)
$EnvFile = Join-Path $PSScriptRoot "../../../.env.github"

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

# Get path to project root directory (for module execution)
$ProjectRoot = Join-Path $PSScriptRoot ".."
$ProjectRoot = Resolve-Path $ProjectRoot

Write-Host "Starting mcp-gh-project MCP server..." -ForegroundColor Cyan
Write-Host "Python: $PythonPath" -ForegroundColor Gray
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Gray

# Launch Python MCP server with environment variables
# Use -m to run as module (enables relative imports)
Set-Location $ProjectRoot
& $PythonPath -m src.server

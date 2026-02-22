$pythonexe = "C:\Users\sha1r\.myenv\Scripts\python.exe"
# Input the absolute path of your Python executable, i.e., "C:\Users\username\.myenv\Scripts\python.exe",
# or leave it empty to use the project's default virtual environment,
# or let the script automatically create a .venv by uv.
# Python >=3.11 required.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# This section is not interchangeable with below ones.
$projectRoot = (Resolve-Path "$PSScriptRoot/..").Path
$toolchainPath = Join-Path $PSScriptRoot "toolchain.py"
Push-Location $projectRoot

# Ensure settings.toml exists.
if (-not (Test-Path -Path ".\settings.toml" -PathType Leaf)) {
    Copy-Item -Path ".\tools\settings.example.toml" -Destination ".\settings.toml" -Force
    Read-Host "Created settings.toml from template. Please manually configure settings.toml and run this script again. Press Enter to exit."
    exit 1
}

# If $pythonexe is empty, check for pyvenv.
if ([string]::IsNullOrWhiteSpace($pythonexe)) {
    # Checking frequent pyvenv location.
    $venvPath = @('.venv', 'venv', '.env', 'env', '.pyenv', 'pyenv') | ForEach-Object { Join-Path $projectRoot "$_\Scripts\python.exe" }
    $firstPath = $venvPath | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($firstPath) { $pythonexe = $firstPath }
    else {
        # Checking every possible pyvenv location.
        $venvPath = Get-ChildItem -Directory | ForEach-Object { Join-Path $_.FullName "Scripts\python.exe" }
        $firstPath = $venvPath | Where-Object { Test-Path $_ } | Select-Object -First 1
        if ($firstPath) { 
            Write-Host "You can manually configure the absolute path of your Python executable at the beginning of this script to avoid automatic searching for Python virtual environment." -ForegroundColor Yellow
            $pythonexe = $firstPath 
        }
        else {
            Write-Host "No Python executable found."
            if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
                Write-Host "No uv found. Press Y to install uv (a modern lightweight Python package manager, install via winget) and automatically create a Python virtual environment to continue. Press other key to exit so you can manually configure the absolute path of your Python executable at the beginning of this script, or create a Python virtual environment at root directory to skip uv."
                if ([System.Console]::ReadKey($true).Key -eq 'Y') {
                    winget install --id=astral-sh.uv -e
                    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
                }
                else { exit 1 }
            }
            # uv found.
            $venvPath = Read-Host "Creating a Python virtual environment by uv. Name your environment or leave blank to skip"
            if ($venvPath) {
                & uv venv $venvPath
                $pythonexe = Join-Path $venvPath "Scripts\python.exe"
            }
            else { exit 1 }
        }
    }
}

Write-Host "Using Python executable at: $pythonexe"
if ((& $pythonexe --version 2>&1) -notmatch "3\.1[1-9]") {
    Read-Host "Python 3.11+ required. Press Enter to exit." -ForegroundColor Red
    exit 1 
}

# To do, or not to do, that is the question.
Write-Host "Press Y to keep window open after execution. Press other key to immediately close the window once complete."
$keepWindowOpen = [System.Console]::ReadKey($true).Key -eq 'Y'
$pythonArgs = @($toolchainPath)
Write-Host "Press Y to delete automatically generated folder and file. Press other key to skip."
if ([System.Console]::ReadKey($true).Key -eq 'Y') { $pythonArgs += "--init" }
if ($env:MOONSHOT_API_KEY) {
    Write-Host "Press Y to run tokenizer. Press other key to skip."
    if ([System.Console]::ReadKey($true).Key -eq 'Y') { $pythonArgs += "--tokenizer" }
}
else { Write-Host "No environment variable MOONSHOT_API_KEY found. Tokenizer skipped." -ForegroundColor Yellow }
& $pythonexe @pythonArgs
if ($keepWindowOpen) { Read-Host "Press Enter to exit." }
exit 0

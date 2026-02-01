$pythonexe = ""
# Leave empty to use the project's default virtual environment or create one.
# Or input the absolute path of your Python executable, i.e., "C:\Users\username\myenv\Scripts\python.exe". 
# Python >=3.11 required.

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$toolchainPath = Join-Path $scriptDir "toolchain.py"
Push-Location $projectRoot

# Check for winget
if (-not (Get-Command "winget" -ErrorAction SilentlyContinue)) {
    Write-Host "winget not detected. Please install App Installer (Search in Microsoft Store)." -ForegroundColor Red
    exit 1
}

# Check for uv, install if missing
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "uv not detected. Installing via winget..."
    winget install astral-sh.uv --source winget --accept-package-agreements --accept-source-agreements
    Write-Host "uv installed. Please restart this script in a new terminal."
    Read-Host "Press any key to exit"
    exit
}

# Handle Python executable
# If $pythonexe is empty, check for .venv. If not found, create it using uv, then set path.
if ([string]::IsNullOrWhiteSpace($pythonexe)) {
    $venvPath = Join-Path $projectRoot ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "No virtual environment found. Creating one..."
        uv venv
    }
    # Set the path to the python executable inside the .venv
    $pythonexe = Join-Path $venvPath "Scripts\python.exe"
}
Write-Host "Using Python executable at: $pythonexe"

# Ensure settings.toml exists
if (-not (Test-Path -Path ".\settings.toml" -PathType Leaf)) {
    Copy-Item -Path ".\tools\settings.example.toml" -Destination ".\settings.toml" -Force
    Write-Host "Created settings.toml from template. Please config settings.toml manually and run this script again."
    Read-Host "Press any key to exit"
    exit
}

# Handle Moonshot API Key
$MOONSHOT_API_KEY = [Environment]::GetEnvironmentVariable("MOONSHOT_API_KEY", "User")
if (-not $MOONSHOT_API_KEY) {
    $MOONSHOT_API_KEY = $false
    Write-Host "User environment variable `MOONSHOT_API_KEY` wasn't detected. Tokenizer skipped. If you need to use this feature, please configure user environment variable `MOONSHOT_API_KEY`." -ForegroundColor Yellow
}

# Interactive prompts
$response = Read-Host "Do you want to init? [N/y]"
$doInit = $response -eq "Y" -or $response -eq "y"

if ($MOONSHOT_API_KEY) {
    $response = Read-Host "Do you want to do tokenizer? [N/y]"
    if ( -not ($response -eq "Y" -or $response -eq "y")) {
        $MOONSHOT_API_KEY = $false
    }
    else {
        uv pip install tomli-w --python $pythonexe
    }
}

# Run toolchain
uv run --python $pythonexe python $toolchainPath $doInit.ToString() $MOONSHOT_API_KEY.ToString()

# Exit script
if ($MOONSHOT_API_KEY) {
    Read-Host "Press any key to exit"
}
exit
<#
.SYNOPSIS
Start doc-workflow toolchain script

.DESCRIPTION
Automatically find/install Python environment (uv preferred), and interactively run workflow:
1. Ask whether to initialize (delete auto-generated folders and files)
2. Ask whether to run tokenizer (requires MOONSHOT_API_KEY)
3. Run toolchain.py once with --clear --combine and optional --init/--tokenizer

The behavior of this script depends on its absolute path, regardless of launch location and current working directory.
#>

$settings_toml = ".\settings.toml"

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Exit-WithPrompt {
    <#
    .SYNOPSIS
    Display prompt message and wait for user to press Enter before exiting

    .PARAMETER Message
    Message to display before exiting (optional)

    .PARAMETER ExitCode
    Exit code (default is 1)
    #>
    param(
        [string]$Message = "",
        [int]$ExitCode = 1
    )
    if ($Message) {
        Write-Host $Message -ForegroundColor Red
    }
    Read-Host "Press Enter to exit"
    exit $ExitCode
}

# This section is not interchangeable with below ones.
$projectRoot = (Resolve-Path "$PSScriptRoot/..").Path
$toolchainPath = Join-Path $PSScriptRoot "toolchain.py"
Push-Location $projectRoot

# Ensure $settings_toml exists.
if (-not (Test-Path -Path $settings_toml -PathType Leaf)) {
    Copy-Item -Path ".\tools\example.toml" -Destination $settings_toml -Force
    Exit-WithPrompt "Created $settings_toml from template. Please manually configure it and run this script again."
}

# Find Python executable: try uv first, then python
$pythonPrefix = @()

# Try uv first - trust uv to provide the correct Python environment
if (Get-Command "uv" -ErrorAction SilentlyContinue) {
    try {
        $versionOutput = & uv run python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonPrefix = @("uv", "run")
            Write-Host "Using uv: $versionOutput"
        }
    }
    catch {
        # uv failed, try regular python
    }
}

# If uv didn't work, try regular python
if (-not $pythonPrefix) {
    if (Get-Command "python" -ErrorAction SilentlyContinue) {
        try {
            $versionOutput = & python --version 2>&1
            if ($versionOutput -match "3\.1[1-9]") {
                $pythonPrefix = @("python")
                Write-Host "Using python: $versionOutput"

                # Ensure typer is installed for native python
                Write-Host "Ensuring typer is installed..."
                & python -m pip install --quiet "typer>=0.15.0"
                if ($LASTEXITCODE -ne 0) {
                    Exit-WithPrompt "Failed to install typer"
                }
                Write-Host "typer is ready."
            }
            else {
                Exit-WithPrompt "Python 3.11+ required, found: $versionOutput"
            }
        }
        catch {
            Exit-WithPrompt "Failed to run python"
        }
    }
    else {
        # Try to install uv via winget if available
        if (Get-Command "winget" -ErrorAction SilentlyContinue) {
            Write-Host "No python or uv found. Attempting to install uv via winget..." -ForegroundColor Yellow
            try {
                winget install astral-sh.uv -e --accept-package-agreements --accept-source-agreements
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "uv installed successfully. Refreshing environment variables..." -ForegroundColor Green

                    # Refresh environment variables from machine and user
                    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

                    # Try uv again
                    if (Get-Command "uv" -ErrorAction SilentlyContinue) {
                        $versionOutput = & uv run python --version 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            $pythonPrefix = @("uv", "run")
                            Write-Host "Using uv: $versionOutput"
                        }
                    }

                    if (-not $pythonPrefix) {
                        Exit-WithPrompt "Failed to use uv after installation."
                    }
                }
                else {
                    Exit-WithPrompt "Failed to install uv via winget (exit code: $LASTEXITCODE)."
                }
            }
            catch {
                Exit-WithPrompt "Error during uv installation: $_"
            }
        }
        else {
            Exit-WithPrompt "No python or uv found. Please install Python 3.11+ or uv."
        }
    }
}

# Collect user choices first
$doInit = $false
$doTokenizer = $false

# Ask if user wants to init first
Write-Host "Press Y to delete automatically generated folder and file. Press other key to skip"
if ([System.Console]::ReadKey($true).Key -eq 'Y') {
    $doInit = $true
}

# Ask if user wants to run tokenizer
if ($env:MOONSHOT_API_KEY) {
    Write-Host "Press Y to run tokenizer. Press other key to skip"
    if ([System.Console]::ReadKey($true).Key -eq 'Y') {
        $doTokenizer = $true
    }
}
else {
    Write-Host "No environment variable MOONSHOT_API_KEY found. Tokenizer skipped." -ForegroundColor Yellow
}

# Build arguments - always include --clear and --combine
$allArgs = $pythonPrefix + @($toolchainPath, "--config", $settings_toml, "--clear", "--combine")
if ($doInit) {
    $allArgs += "--init"
}
if ($doTokenizer) {
    $allArgs += "--tokenizer"
}

# Run toolchain.py once
& $allArgs[0] $allArgs[1..($allArgs.Count - 1)]
if ($LASTEXITCODE -ne 0) {
    Exit-WithPrompt "Workflow failed" $LASTEXITCODE
}

Read-Host "Press Enter to exit"
exit 0

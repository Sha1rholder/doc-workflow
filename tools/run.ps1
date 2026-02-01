$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$toolchainPath = Join-Path $scriptDir "toolchain.py"
Push-Location $projectRoot

$MOONSHOT_API_KEY = [Environment]::GetEnvironmentVariable("MOONSHOT_API_KEY", "User")
if (-not $MOONSHOT_API_KEY) {
    $MOONSHOT_API_KEY = $false
    Write-Host "User environment variable `MOONSHOT_API_KEY` wasn't detected. Tokenizer skipped. If you need to use this feature, please configure user environment variable `MOONSHOT_API_KEY`." -ForegroundColor Yellow
}

$response = Read-Host "Do you want to init? [N/y]"
$doInit = $response -eq "Y" -or $response -eq "y"

if ($MOONSHOT_API_KEY) {
    $response = Read-Host "Do you want to do tokenizer? [N/y]"
    if ( -not ($response -eq "Y" -or $response -eq "y")) {
        $MOONSHOT_API_KEY = $false
    }
}

uv run --python "C:\Users\sha1r\myenv\Scripts\python.exe" python $toolchainPath $doInit.ToString() $MOONSHOT_API_KEY.ToString()
Pop-Location

if ($MOONSHOT_API_KEY) {
    Read-Host "Press any button to exit"
}
Read-Host "Press any button to exit"
exit
$settingsPath = Join-Path $PSScriptRoot "..\settings.toml"
$examplePath = Join-Path $PSScriptRoot "settings example.toml"
if (-not (Test-Path $settingsPath)) {
    Copy-Item $examplePath $settingsPath
}

$content = Get-Content $settingsPath -Raw
if ($content -match '(?s)\[user\].*?pyenv\s*=\s*["'']([^"'']+)["'']') {
    $pyenv = $matches[1].Replace('/', '\')
    & "$pyenv\Scripts\python.exe" (Join-Path $PSScriptRoot "toolchain.py")
}

# 文档工作流

基于PowerShell和Python自动化，面向LLM协作的轻量级的文档工作流，具有清除html注释、合并文档为LLM友好形式、计算tokens等功能

在项目根目录运行`run.ps1`或在任何地方运行以下内容（可保存为一个.ps1文件）即可生成LLM友好的文档toolchain

```ps1
$targetDir = "xxx" # 项目母文件夹的**绝对路径**
$scriptPath = Join-Path $targetDir "tools\run.ps1"
Push-Location $targetDir
try {
    & $scriptPath
}
finally {
    Pop-Location
}
exit
```

首次运行后编辑`settings.toml`中的`pyenv`为自己的Python虚拟环境路径，如果你需要快速统计tokens的话，需要申请一个Kimi的API并替换`MOONSHOT_API_KEY`

编辑`settings.toml`即可高度自定义工作流

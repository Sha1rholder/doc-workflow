# 文档工作流

在项目根目录运行`run.ps1`或在任何地方运行以下内容（可保存为一个.ps1文件）即可生成LLM友好的文档toolchain

```ps1
$targetDir = "C:\Users\sha1r\Desktop\workflow\" # 项目母文件夹的绝对路径
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

首次运行后编辑`settings.toml`即可自定义工作流并定制tokenizer

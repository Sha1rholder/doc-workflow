# doc-workflow

超轻量Markdown文档处理工作流自动化工具，用于清理、合并文档并估算token数量。适用于频繁与LLM交互但不想依赖各种臃肿的闭源工具的创作者

## 功能特性

- **清理注释** - 为根目录中所有Markdown文件创建一个不含HTML注释的版本
- **合并文档** - 将多个Markdown文件合并为XML格式
- **Moonshot Tokenizer** - 调用Moonshot API估算文件tokens

## 使用

运行`tools/run.ps1`后按需编辑`settings.toml`，再次运行`tools/run.ps1`

在任何地方运行`tools/run.ps1`效果都相同，因为脚本会自动查找项目绝对路径。因此，可以给该脚本创建快捷方式放在任何你喜欢的地方

直接运行`tools/run.ps1`会使用Python包管理器uv在项目根目录创建一个Python虚拟环境`.venv`，但你也可以编缉`tools/run.ps1`的第一行以手动指定python.exe

对于已存在的项目，直接复制整个`tools/`文件夹到你的项目根目录即可

如果要使用Moonshot Tokenizer，请在Moonshot AI官网申请一个API Key并添加到用户环境变量`MOONSHOT_API_KEY`

## 目录结构

```
doc-workflow/
└── tools/             # 工具目录
    ├── run.ps1        # PowerShell启动脚本
    ├── toolchain.py   # 核心Python脚本
    └── settings.example.toml # 配置文件模板
```

## settings.toml

- `combinations` - 定义文档合并规则
  - `output` - 输出文件名（不含扩展名）
  - `inputs` - 输入文件列表
- `tokenizer` - 定义需要估算token的文件
  - `files` - 文件路径列表

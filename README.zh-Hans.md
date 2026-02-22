# doc-workflow

知识库整理脚本。能够指定文档清除html注释，合并为xml，以及用Kimi K2.5的分词器计算tokens

将碎片化的文档合并为xml可以在对agent保留目录结构信息的同时大幅减少每次提问产生的工具调用次数并方便控制内容可见度，这样做的好处包括：1. 大幅减少每次提问消耗的tokens；2. 大幅减轻“长上下文腐烂”现象；3. 大幅减少节省agent思考的时间

用户无需任何编程知识就可以交互式使用该脚本，有一定基础的用户还可以将其轻易集成到CI/CD中

## 使用

首次运行`tools/run.ps1`后按需编辑`settings.toml`，再次运行`tools/run.ps1`

在任何地方运行`tools/run.ps1`效果都相同，因为脚本会自动查找项目绝对路径。因此，可以给该脚本创建快捷方式放在任何你喜欢的地方并轻易集成到任何CI/CD管线中

对于已存在的项目，直接复制整个`tools/`文件夹到项目根目录即可

如果要计算tokens，请在Moonshot AI官网申请一个API Key并添加到环境变量`MOONSHOT_API_KEY`

## 工具目录

```txt
doc-workflow/
└─ tools/             # 工具目录
   ├── run.ps1        # PowerShell启动脚本
   ├── toolchain.py   # 核心Python脚本
   └── settings.example.toml # 配置文件模板
```

## settings.toml

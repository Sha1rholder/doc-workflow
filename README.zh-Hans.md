# doc-workflow

知识库整理脚本。能够按需批量清除html注释，合并为xml，以及用Kimi K2.5的分词器计算tokens

将碎片化的文档合并为xml可以在对agent保留目录结构信息的同时大幅减少每次提问产生的工具调用次数并方便控制内容可见度，这样做的好处包括：1. 大幅减少每次提问消耗的tokens；2. 大幅减轻“长上下文腐烂”现象；3. 大幅减少节省agent思考的时间

无需任何编程知识就可以通过`run.ps1`交互式使用该脚本。有一定基础的用户还可以将`toolchain.py`轻易集成到CI/CD中

具体实现：[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Sha1rholder/doc-workflow)

## 使用方法

1. 复制整个`tools/`文件夹到项目根目录
2. 运行`tools/run.ps1`
3. 编辑`settings.toml`
4. 再运行`tools/run.ps1`

`tools/run.ps1`的效果取决于其绝对路径，和它在哪启动/当前工作目录无关

如果要启用tokenizer，请创建一个环境变量`MOONSHOT_API_KEY`（用户或系统级都行），并在月之暗面官网<https://platform.moonshot.cn>（海外版官网<https://platform.moonshot.ai>）申请一个API Key并添加到`MOONSHOT_API_KEY`

如果你是在<https://platform.moonshot.ai>申请的API Key，请记得修改`settings.toml`中的`[tokenizer].endpoint`

## 工具目录

```txt
doc-workflow/
└─ tools/                   # 工具目录
   ├─ run.ps1               # PowerShell启动脚本
   ├─ toolchain.py          # 核心Python脚本
   └─ settings.example.toml # 配置文件模板
```

## settings.toml

`settings.toml`是`toolchain.py`的配置文件，可以用记事本编缉

| 配置项 | 说明 |
| --- | --- |
| derived_folder | 输出文件夹，存放处理后的文件 |
| tokens_csv | Token统计记录文件 |
| remove_comments | 需要清除HTML注释的文件列表 |
| [[combinations]] | 文档合并配置，可定义多个组合，支持链式合并 |
| [tokenizer].endpoint | Tokenizer API endpoint |
| [tokenizer].files | 需要计算tokens的文件列表 |

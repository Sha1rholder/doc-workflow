# doc-workflow

知识库整理工具链。能够批量清除html注释，合并文件为xml，以及用Kimi K2.5的分词器计算tokens

无需任何编程知识就可以通过`run.ps1`交互式使用该脚本。有一定基础的用户还可以将`toolchain.py`轻易集成到workflow中

## How It Works

使用Claude Code之类的agent工具协助浏览大量碎片化的文档时，常难以精准控制agent每轮对话加载的上下文——你永远不知道agent下一秒会Read哪个你不想让它在这一轮会话中看到的内容。这不仅浪费tokens，还容易导致模型注意力涣散、降智，即“长上下文腐烂”

另一方面，当需要agent加载多个特定上下文时，它又经常要通过多次工具调用才能加载完所有内容，而每次工具调用都意味着一个新的请求，要把所有上文和CoT全部重新喂给agent背后的模型，因此每次调用都会成倍增加累计输入的tokens。模型如果能命中上下文缓存还勉强，要是不幸没有……那你最好不是api按量计费

针对以上问题，本工具链通过“让用户手动设置文件组合->把原本可能散在各处的文件视为xml元素->在保留路径信息的情况下将它们结合为单个xml文件”的朴素方式实现了显著的规避作用。简单来说，“你想让agent发现什么，就将组合好的文件一次性喂给它”。综上，本工具链可以：

- 减少agent发起请求的轮次，“从提问到回答”更快
- 减少每轮对话消耗的tokens，减轻agent探索工作目录导致的“长上下文腐烂”现象
- 避免agent看到不该看的内容（这对写小说和角色扮演来说尤其重要）
- ……

除此以外，本工具链还有批量清除markdown中的html注释并保存为副本、批量计算tokens、嵌套xml并在合并文件阶段添加注释以向agent传递文件之间的逻辑关系信息等“高级”功能

为什么要用xml：<https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags>

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
└─ tools/          # 工具目录
   ├─ run.ps1      # PowerShell启动脚本
   ├─ toolchain.py # 主程序入口，协调各模块工作
   ├─ init.py      # 初始化模块，清理输出目录和tokens.csv
   ├─ compare.py   # 文件比较工具，检查文件是否需要更新
   ├─ clear.py     # html注释清除工具
   ├─ combine.py   # 文件合并工具，将多个文件合并为xml
   ├─ tokenizer.py # Moonshot tokenizer
   └─ example.toml # 配置文件模板
```

## settings.toml

`settings.toml`是`toolchain.py`的配置文件，由`example.toml`复制生成，可以用记事本编缉。如果你不想用这个文件名，也可以在`run.ps1`中修改

| 配置项 | 说明 |
| --- | --- |
| cleared_folder | 存放清除html注释后的文件目录 |
| delete_cleared | 是否在执行完后删除cleared_folder |
| combined_folder | 存放结合后的xml文件目录 |
| combined_extension | 输出文件的后缀名 |
| tokens_csv | Token统计记录文件 |
| remove_comments | 需要清除html注释的文件列表 |
| [[combinations]] | 文档合并配置，可定义多个组合，支持链式合并 |
| [tokenizer].endpoint | Tokenizer API endpoint |
| [tokenizer].files | 需要计算tokens的文件列表 |

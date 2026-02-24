[中文版README](./README.zh-Hans.md)

# doc-workflow

A knowledge base organization script. It can remove HTML comments, merge files into XML, and calculate tokens with Kimi K2.5 tokenizer in bulk.

Merging fragmented documents into XML can preserve directory structure information for the agent while significantly reducing the number of tool calls per query and facilitating content visibility control. The benefits of doing so include: 1. Significantly reducing token consumption per query; 2. Alleviating the "long context decay" phenomenon; 3. Saving your time waiting for agents' response.

You can interactively use this script via `run.ps1` without any programming knowledge. and users with some technical background can also easily integrate `toolchain.py` into CI/CD pipelines.

Detailed implementation explained: [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Sha1rholder/doc-workflow)

## How to Use

1. Copy the entire `tools/` folder to your project's root directory.
2. Run `tools/run.ps1`.
3. Edit `settings.toml`.
4. Run `tools/run.ps1` again.

The behavior of `run.ps1` depends on its absolute path and is irrelevant to where it is launched and current working directory.

To enable tokenizer, please create an environment variable `MOONSHOT_API_KEY` (both user and system level are good). Then apply for an API Key on Moonshot AI platform <https://platform.moonshot.ai> (for those in China: <https://platform.moonshot.cn>). Then add your API Key to `MOONSHOT_API_KEY`.

If you applied your API Key on <https://platform.moonshot.ai>, remember to change `[tokenizer].endpoint` in `settings.toml`.

## Tool Directory

```txt
doc-workflow/
└─ tools/                   # Tool directory
   ├─ run.ps1               # PowerShell startup script
   ├─ toolchain.py          # Core Python script
   ├─ tokenizer.py          # Moonshot tokenizer
   └─ settings.example.toml # Configuration file template
```

## settings.toml

`settings.toml` is the configuration file for `toolchain.py` and can be edited with Windows Notepad.

| Configuration Item | Description |
| --- | --- |
| cleared_folder | Output folder for storing HTML-comments-removed files |
| delete_cleared | Whether to delete cleared_folder after execution |
| combined_folder | Output folder for storing combined XML files |
| combined_extension | File extension for the output files |
| tokens_csv | Token statistics record file |
| remove_comments | List of files that need HTML comments removed |
| [[combinations]] | Document merging configuration; allows defining multiple combinations and supports chained merging |
| [tokenizer].endpoint | Tokenizer API endpoint |
| [tokenizer].files | List of files to calculate tokens for |

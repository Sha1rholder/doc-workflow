[中文](./README.zh-Hans.md)

# doc-workflow

A knowledge base organization toolchain. Can bulk remove html comments, merge files into xml, and calculate tokens with Kimi K2.5's tokenizer.

You can use this script interactively via `run.ps1` without any programming knowledge. Users with some technical background can also easily integrate `toolchain.py` into their workflows.

## How It Works

When using agent tools like Claude Code to browse through large amounts of fragmented documentation, it's often difficult to precisely control the context the agent loads in each conversation—you never know what file the agent might Read next that you didn't want it to see in this session. This not only wastes tokens, but also easily leads to scattered attention and reduced model performance, also known as "long context decay".

On the other hand, when you need the agent to load multiple specific contexts, it often has to make multiple tool calls to load everything. And each tool call means a new request where you have to feed all the previous context and CoT back to the agent's model, so each call exponentially increases the total input tokens. If the model hits the context cache, it's manageable, but if it doesn't... well, hopefully you're not on pay-as-you-go API pricing.

To address these issues, this toolchain provides a simple yet effective approach: "let users manually set file combinations -> treat files scattered in different locations as xml elements -> combine them into a single xml file while preserving path information". Simply put, "whatever you want the agent to discover, feed it the combined files all at once". Overall, this toolchain can:

- Reduce the number of agent request rounds, making "from question to answer" faster
- Reduce token consumption per conversation, alleviating the "long context decay" caused by agents exploring the work directory
- Prevent agents from seeing content they shouldn't (this is especially important for writing novels and role-playing)
- ...

Additionally, this toolchain has "advanced" features like bulk removing html comments from markdown and saving copies, bulk token calculation, nested xml, and adding comments during the file merging phase to convey logical relationship information between files to the agent.

Why xml: <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags>

Detailed implementation: [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Sha1rholder/doc-workflow)

## How to Use

1. Copy the entire `tools/` folder to your project root directory
2. Run `tools/run.ps1`
3. Edit `settings.toml`
4. Run `tools/run.ps1` again

The behavior of `tools/run.ps1` depends on its absolute path and is independent of where it's launched or the current working directory.

To enable the tokenizer, please create an environment variable `MOONSHOT_API_KEY` (either user or system level works), and apply for an API Key from Moonshot's official website <https://platform.moonshot.ai> (China site <https://platform.moonshot.cn>), then add your API Key to `MOONSHOT_API_KEY`.

If you applied for your API Key at <https://platform.moonshot.ai>, remember to modify `[tokenizer].endpoint` in `settings.toml`.

## Tool Directory

```txt
doc-workflow/
└─ tools/          # Tool directory
   ├─ run.ps1      # PowerShell startup script
   ├─ toolchain.py # Main program entry, coordinates all modules
   ├─ init.py      # Initialization module, cleans output directories and tokens.csv
   ├─ compare.py   # File comparison tool, checks if files need updating
   ├─ clear.py     # html comment removal tool
   ├─ combine.py   # File merging tool, combines multiple files into xml
   ├─ tokenizer.py # Moonshot tokenizer
   └─ example.toml # Configuration file template
```

## settings.toml

`settings.toml` is the configuration file for `toolchain.py`, copied from `example.toml`, and can be edited with Notepad. If you don't want to use this filename, you can also modify it in `run.ps1`.

| Configuration Item | Description |
| --- | --- |
| cleared_folder | Directory for storing files with html comments removed |
| delete_cleared | Whether to delete cleared_folder after execution |
| combined_folder | Directory for storing combined xml files |
| combined_extension | Output file extension |
| tokens_csv | Token statistics record file |
| remove_comments | List of files that need html comments removed |
| [[combinations]] | Document merging configuration, multiple combinations can be defined, supports chaining |
| [tokenizer].endpoint | Tokenizer API endpoint |
| [tokenizer].files | List of files to calculate tokens for |

[中文](README_zh.md)

# doc-workflow

An ultra-lightweight automated Markdown document processing workflow. Used for cleaning and merging documents as well as estimating the number of tokens. Ideal for creators who frequently interact with LLMs but don't want to rely on various bulky, closed-source tools.

Automated Markdown document processing workflow tool for cleaning, merging documents, and estimating token counts.

## Features

- **Clean Comments** - Creates a version of all Markdown files in the root directory without HTML comments.
- **Merge Documents** - Merges multiple Markdown files into a single XML format.
- **Moonshot Tokenizer** - Calls the Moonshot API to estimate file tokens.

## Usage

Run `tools/run.ps1`, edit `settings.toml` as needed, and then run `tools/run.ps1` again.

Running `tools/run.ps1` from any location yields the same result because the script automatically identifies the project's absolute path. Therefore, you can create a shortcut to this script and place it anywhere you prefer.

Running `tools/run.ps1` directly will use the Python package manager `uv` to create a Python virtual environment `.venv` in the project root. However, you can also edit the first line of `tools/run.ps1` to manually specify the path to `python.exe`.

For existing projects, simply copy the entire `tools/` folder into the root directory of your project.

To use the Moonshot Tokenizer, please apply for an API Key on the Moonshot AI official website and add it to your user environment variables as `MOONSHOT_API_KEY`.

## Directory Structure

```
doc-workflow/
└── tools/                # Tools directory
    ├── run.ps1           # PowerShell startup script
    ├── toolchain.py      # Core Python script
    └── settings.example.toml # Configuration template
```

## settings.toml

- `combinations` - Defines document merging rules
  - `output` - Output filename (without extension)
  - `inputs` - List of input files
- `tokenizer` - Defines files for token estimation
  - `files` - List of file paths

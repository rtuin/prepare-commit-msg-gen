# Git Commit Message Generator

A tool that helps generate meaningful commit messages for your Git repositories using LLMs.

## Installation

### From Homebrew (for users)
You can install this package using Homebrew:

```bash
brew install rtuin/tools/prepare-commit-msg-gen
```

### Local Development Installation
To install the package locally for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/rtuin/prepare-commit-msg-gen.git
   cd prepare-commit-msg-gen
   ```

2. Install Poetry if you haven't already: https://python-poetry.org/docs/#installation

3. Install the package in editable mode:
   ```bash
   poetry install
   poetry build
   pip install -e .
   ```

4. Test the package:
   ```bash
   touch test-message.txt
   prepare-commit-msg-gen test-message.txt
   ```


## Setting up the Git Hook

After installing the package, you need to set up the pre-commit hook in your Git repository:

1. Navigate to your Git repository:
   ```bash
   cd your-repository
   ```

2. Create a new pre-commit hook:
   ```bash
   mkdir -p .git/hooks
   echo '#!/bin/sh
   prepare-commit-msg-gen "$1"' > .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/prepare-commit-msg
   ```

## Usage

Once installed and set up, the hook will automatically run every time you create a new commit. It will analyze your changes and suggest a meaningful commit message.

## Configuration

The tool can be configured using environment variables:

### LLM Provider Configuration
- `PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER`: Choose the LLM provider to use (default: "ollama")
  - Supported values: "ollama", "openai"
- `PREPARE_COMMIT_MSG_GEN_LLM_MODEL`: Specify the model to use
  - For Ollama: defaults to "qwen2.5-coder:7b"
  - For OpenAI: defaults to "gpt-4o"

### Ollama-specific Configuration
- `PREPARE_COMMIT_MSG_GEN_OLLAMA_BASE_URL`: Set the base URL for your Ollama instance (default: "http://localhost:11434")

### OpenAI-specific Configuration
- `OPENAI_API_KEY`: Your OpenAI API key (required when using OpenAI provider)

## Troubleshooting

### Hook Not Running

If the hook is not running when you make commits, ensure that:

1. The hook is installed in the correct hooks directory. Git uses the directory specified by `core.hooksPath` configuration. By default, this is `.git/hooks/` in your repository. You can check your hooks path with:
   ```bash
   git config core.hooksPath
   ```

2. If you've configured a custom hooks path, make sure to install the hook in that directory instead of `.git/hooks/`.

3. The hook file has executable permissions:
   ```bash
   chmod +x <hooks-path>/prepare-commit-msg
   ```

## Development

This project uses Poetry for dependency management. To set up a development environment:

1. Clone the repository
2. Install Poetry if you haven't already: https://python-poetry.org/docs/#installation
3. Install dependencies:
   ```bash
   poetry install
   ```

4. Run tests:
   ```bash
   poetry run pytest
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

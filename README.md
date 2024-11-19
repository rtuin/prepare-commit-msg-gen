# Pre-Commit Message Generator

A tool that helps generate meaningful commit messages for your Git repositories using LLMs.

## Installation

### From PyPI (for users)
You can install this package using pip:

```bash
pip install pre-commit-msg-gen
```

### Local Development Installation
To install the package locally for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/rtuin/pre-commit-msg-gen.git
   cd pre-commit-msg-gen
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
   pre-commit-msg-gen test-message.txt
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
   pre-commit-msg-gen "$1"' > .git/hooks/prepare-commit-msg
   chmod +x .git/hooks/prepare-commit-msg
   ```

## Usage

Once installed and set up, the hook will automatically run every time you create a new commit. It will analyze your changes and suggest a meaningful commit message.

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

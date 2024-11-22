#!/usr/bin/env python3
import sys
import os
import subprocess
from typing import Optional
from . import __version__

# from langchain_core.schema import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm_client():
    """Get the LLM client based on configuration."""
    provider = os.getenv("PREPARE_COMMIT_MSG_GEN_LLM_PROVIDER", "ollama").lower()
    
    if provider == "openai":
        model_name = os.getenv("PREPARE_COMMIT_MSG_GEN_LLM_MODEL", "gpt-4o")
        return ChatOpenAI(
            model=model_name,
            temperature=0.1
        )
    
    if provider == "ollama":
        model_name = os.getenv("PREPARE_COMMIT_MSG_GEN_LLM_MODEL", "qwen2.5-coder:7b")
        base_url = os.getenv("PREPARE_COMMIT_MSG_GEN_OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=model_name,
            temperature=0.1,
            base_url=base_url
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")

def get_staged_diff() -> str:
    result = subprocess.run(['git', 'diff', '--cached'], stdout=subprocess.PIPE)
    diff = result.stdout.decode('utf-8')
    return diff

def generate_commit_message(diff: str) -> Optional[str]:
    prompt = f"""
You are an expert software engineer and a helpful assistant that writes clear and concise Git commit messages following the Conventional Commits specification.

Please analyze the following Git diff and summarize the changes in a commit message.

Requirements:
- detect a scope: it usually is a module name (directory only), or empty
- The commit message must be in the format: <type>[optional scope]: <description>
- Use one of the following types: feat, fix, docs, style, refactor, test, chore, perf, ci, build.
- If applicable, include a scope in parentheses after the type.
- The description should be brief (max 72 characters) and in the imperative mood.
- Only generate the commit title, not the body.
- the output must be on a single line in plain text

Use these rules to determine the commit type:
- feat: A new feature
- fix: A bug fix
- chore: Code changes that aren't related to a feature or bug fix
- docs: Documentation changes
- style: Code style changes
- refactor: A change that doesn't add or remove functionality

Diff:
{diff}
    """

    try:
        llm = get_llm_client()
        messages = [
            SystemMessage(content="You are a helpful assistant that writes Git commit messages."),
            HumanMessage(content=prompt)
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return None

def main():
    """Main entry point for the pre-commit message generator."""
    if len(sys.argv) > 1 and sys.argv[1] in ['--version', '-v']:
        print("prepare-commit-msg-gen")
        print(f"  Version {__version__}")
        print("  https://github.com/rtuin/prepare-commit-msg-gen")
        print("  Copyright (c) 2024 Richard Tuin")
        return 0

    # The pre-commit hook receives the path to the commit message file as the first argument
    if len(sys.argv) < 2:
        print("Error: Expected commit message file path as argument", file=sys.stderr)
        sys.exit(1)

    commit_msg_file = sys.argv[1]

    # Exit if committing a merge or amend
    if len(sys.argv) > 2 and sys.argv[2] in ['merge', 'commit']:
        sys.exit(0)

    diff = get_staged_diff()
    if not diff:
        # No job to do. This also triggers during rebase
        sys.exit(0)

    commit_message = generate_commit_message(diff)
    if not commit_message:
        print("Failed to generate commit message.")
        sys.exit(1)

    if not os.path.exists(commit_msg_file):
        print(f"Error: Commit message file {commit_msg_file} does not exist", file=sys.stderr)
        sys.exit(1)

    # Write the commit message to the commit message file
    with open(commit_msg_file, 'w') as f:
        f.write(commit_message)

    return 0

if __name__ == "__main__":
    sys.exit(main())

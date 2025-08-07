from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from rich import print


def load_env(env_file: str | None = None) -> None:
    """
    Load environment variables from a .env file using python-dotenv.

    If env_file is None, it looks for a .env in the project root.
    """
    if env_file is None:
        # Resolve project root as directory containing this file's parent or current working dir
        project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / ".env"
    else:
        env_path = Path(env_file)

    if env_path.exists():
        load_dotenv(env_path)
        print(f"[green]Loaded environment from[/green] {env_path}")
    else:
        print(f"[yellow].env file not found at[/yellow] {env_path}; using existing environment")


if __name__ == "__main__":
    load_env()
    # Example usage: read the OpenAI API key without printing it
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    print(f"OPENAI_API_KEY set: {has_key}")


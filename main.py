# version 0.1
import argparse
from pathlib import Path
import subprocess
import sys


def resolve_args() -> argparse.Namespace:
    cmd_parser = argparse.ArgumentParser(
        description='git-measure, by rhawk117 track and compare the contributions in a repository.'
    )
    cmd_parser.add_argument('-p', '--path', required=True,
                            help='Path to the Git repository')
    cmd_parser.add_argument('-a', '--author', required=True,
                            help='Author name to filter commits')
    return cmd_parser.parse_args()


def check_git() -> None:
    result = subprocess.run(
        ['git', '--version'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    if result.returncode != 0:
        sys.stderr.write(
            "Error: Git is not installed or not found in PATH. Please install Git from https://git-scm.com/downloads and ensure it's added to your system's PATH.\n")
        sys.exit(1)


def validate_git_repository(repo_path: Path) -> None:
    git_dir = repo_path / '.git'
    if not git_dir.is_dir():
        sys.stderr.write(
            f"Error: No .git directory found in the specified path: {repo_path}\n")
        sys.exit(1)


def check_author_exists(repo_path: Path, author: str) -> None:
    try:
        result = subprocess.run(
            ['git', 'log', '--author', author, '--pretty=oneline'],
            cwd=str(repo_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            sys.stderr.write(f"Git error: {result.stderr.strip()}\n")
            sys.exit(1)
        if not result.stdout.strip():
            sys.stderr.write(f"Error: Author '{author}' not found in the repository.\n")
            sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write("Error: Git is not installed or not found in PATH.\n")
        sys.exit(1)


def get_contribution_stats(repo_path: Path, author: str) -> tuple:
    try:
        result = subprocess.run(
            ['git', 'log', '--author', author, '--pretty=tformat:', '--numstat'],
            cwd=str(repo_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            sys.stderr.write(f"Git error: {result.stderr.strip()}\n")
            sys.exit(1)

        insertions = deletions = 0
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            insert, delete, _ = parts
            try:
                insertions += int(insert) if insert.isdigit() else 0
                deletions += int(delete) if delete.isdigit() else 0
            except ValueError:
                continue

        return (insertions, deletions)
    except FileNotFoundError:
        sys.stderr.write("Error: Git is not installed or not found in PATH.\n")
        sys.exit(1)


def display_output(author: str, insertions: int, deletions: int, net_contribution: int) -> None:
    print(f"""
    [>] Author: {author}
    [+] Insertions: {insertions}
    [-] Deletions: {deletions}
    [~] Net Contribution: {net_contribution}
    """)


def main() -> None:
    args = resolve_args()
    repo_path = Path(args.path).resolve()
    author = args.author
    check_git()

    validate_git_repository(repo_path)

    check_author_exists(repo_path, author)

    insertions, deletions = get_contribution_stats(repo_path, author)
    net_contribution = insertions - deletions
    display_output(author, insertions, deletions, net_contribution)


if __name__ == '__main__':
    main()
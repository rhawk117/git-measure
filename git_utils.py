import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Optional
from display import Prompts
from colorama import Fore


class AuthorResults:
    def __init__(self, author: str):
        self.author: str = author
        self.commits: int = 0
        self.insertions: int = 0
        self.deletions: int = 0
        self.net: int = 0
        self.rank: int = 0 

    def add_commit(self, insertions: int, deletions: int):
        self.commits += 1
        self.insertions += insertions
        self.deletions += deletions
        self.net = self.insertions - self.deletions


class GitResults:
    def __init__(self):
        self.contributions = defaultdict(lambda: AuthorResults(author=""))

    def add_contribution(self, author: str, insertions: int, deletions: int):
        if not self.contributions[author].author:
            self.contributions[author].author = author
        self.contributions[author].add_commit(insertions, deletions)

    def get_top_contributors(self, by: str = 'net', top_n: int = 10) -> List[AuthorResults]:
        if by not in ['i', 'd', 'net']:
            by = 'net'
        metric = {
            'i': 'insertions', 
            'd': 'deletions', 
            'net': 'net'
        }[by]
        sorted_contributors = sorted(
            self.contributions.values(),
            key=lambda x: getattr(x, metric),
            reverse=True
        )
        for rank, contributor in enumerate(sorted_contributors[:top_n], start=1):
            contributor.rank = rank
        return sorted_contributors[:top_n]

    def has_contributors(self) -> bool:
        return bool(self.contributions)

    def get_contribution(self, author: str) -> Optional[AuthorResults]:
        return self.contributions.get(author, None)


class GitUtils:
    @staticmethod
    def validate_git(repo_path: Path):
        GitUtils.check_git_installed()
        GitUtils.validate_git_repository(repo_path)

    @staticmethod
    def check_git_installed():
        try:
            result = subprocess.run(
                ['git', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True 
            )
            if result.returncode != 0:
                raise FileNotFoundError
        except FileNotFoundError:
            Prompts.error_prompt(
                "Git is not installed or not found in PATH. Please install Git from https://git-scm.com/downloads and ensure it's added to your system's PATH."
            )
            sys.exit(1)

    @staticmethod
    def validate_git_repository(repo_path: Path):
        git_dir = repo_path / '.git'
        if not git_dir.is_dir():
            Prompts.error_prompt(
                f"No '.git' directory was found in the specified or set path: {repo_path}"
            )
            sys.exit(1)

    @staticmethod
    def fetch_git_data(repo_path: Path, author: Optional[str] = None) -> str:
        if author:
            cmd = ['git', 'log', '--author', author,
                   '--pretty=format:%an', 
                   '--numstat']
        else:
            cmd = ['git', 'log', '--pretty=format:%an', '--numstat']

        try:
            result = subprocess.run(
                cmd,
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            return result.stdout
        except FileNotFoundError:
            Prompts.error_prompt(
                "Git is not installed or not found in PATH."
            )
            sys.exit(1)

    @staticmethod
    def resolve_git_output(git_output: str, git_results: GitResults):
        current_author = None

        for line in git_output.split('\n'):
            if not line.strip():
                continue
            if '\t' not in line:
                current_author = line.strip()
                if current_author not in git_results.contributions:
                    git_results.contributions[current_author] = AuthorResults(
                        author=current_author)
                continue
            if current_author is None:
                continue
            parts = line.split('\t')
            if len(parts) < 3:
                continue
            insert, delete, _ = parts
            try:
                insert = int(insert) if insert.isdigit() else 0
                delete = int(delete) if delete.isdigit() else 0
            except ValueError:
                insert = 0
                delete = 0
            git_results.add_contribution(current_author, insert, delete)

# git.py

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
        metric = {'i': 'insertions', 'd': 'deletions', 'net': 'net'}[by]
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


class GitData:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.authors: List[str] = []
        self.creation_date: str = ''
        self.branches: List[str] = []
        self.last_commit_date: str = ''
        self.predominant_language: str = ''
        self.git_results = GitResults()
        self.fetch_all_data()

    def fetch_all_data(self):
        self.authors = GitUtils.get_authors(self.repo_path)
        self.creation_date = GitUtils.get_creation_date(self.repo_path)
        self.branches = GitUtils.get_branches(self.repo_path)
        self.last_commit_date = GitUtils.get_last_commit_date(self.repo_path)
        self.predominant_language = GitUtils.get_predominant_language(
            self.repo_path)
        git_output = GitUtils.fetch_git_data(self.repo_path)
        GitUtils.resolve_git_output(git_output, self.git_results)

    def create_git_results(self) -> GitResults:
        return self.git_results

    def create_author_results(self) -> GitResults:
        return self.git_results


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
                f"No .git directory found in the specified path: {repo_path}"
            )
            sys.exit(1)

    @staticmethod
    def fetch_git_data(repo_path: Path, author: Optional[str] = None) -> str:
        if author:
            cmd = ['git', 'log', '--author', author,
                   '--pretty=format:%an', '--numstat']
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
            else:
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

    @staticmethod
    def get_authors(repo_path: Path) -> List[str]:
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%an'],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            authors = list(set(result.stdout.strip().split('\n')))
            return authors
        except FileNotFoundError:
            Prompts.error_prompt("Git is not installed or not found in PATH.")
            sys.exit(1)

    @staticmethod
    def get_creation_date(repo_path: Path) -> str:
        try:
            result = subprocess.run(
                ['git', 'log', '--reverse', '--pretty=format:%ad', '-n', '1'],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            return result.stdout.strip()
        except FileNotFoundError:
            Prompts.error_prompt("Git is not installed or not found in PATH.")
            sys.exit(1)

    @staticmethod
    def get_branches(repo_path: Path) -> List[str]:
        try:
            result = subprocess.run(
                ['git', 'branch', '--all', '--no-color'],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            branches = [line.strip().lstrip('* ').strip()
                        for line in result.stdout.strip().split('\n') if line]
            return branches
        except FileNotFoundError:
            Prompts.error_prompt("Git is not installed or not found in PATH.")
            sys.exit(1)

    @staticmethod
    def get_last_commit_date(repo_path: Path) -> str:
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=format:%ad'],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            return result.stdout.strip()
        except FileNotFoundError:
            Prompts.error_prompt("Git is not installed or not found in PATH.")
            sys.exit(1)

    @staticmethod
    def get_predominant_language(repo_path: Path) -> str:
        try:
            result = subprocess.run(
                ['git', 'ls-files'],
                cwd=str(repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            files = result.stdout.strip().split('\n')
            language_counts = defaultdict(int)
            for file in files:
                extension = Path(file).suffix.lower()
                language = GitUtils.map_extension_to_language(extension)
                if language:
                    language_counts[language] += 1
            if not language_counts:
                return "Unknown"
            predominant_language = max(
                language_counts, key=language_counts.get)
            return predominant_language
        except FileNotFoundError:
            Prompts.error_prompt("Git is not installed or not found in PATH.")
            sys.exit(1)

    @staticmethod
    def map_extension_to_language(extension: str) -> Optional[str]:
        extension_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.c': 'C',
            '.cpp': 'C++',
            '.cs': 'C#',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.php': 'PHP',
            '.ts': 'TypeScript',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.m': 'Objective-C',
            '.rs': 'Rust',
            '.scala': 'Scala',
            '.pl': 'Perl',
            '.sh': 'Shell',
            '.html': 'HTML',
            '.css': 'CSS',
            '.json': 'JSON',
            '.xml': 'XML',
        }
        return extension_mapping.get(extension, None)

    @staticmethod
    def check_author_exists(repo_path: Path, author: str):
        """
        Checks if the specified author exists in the repository.
        """
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
                Prompts.error_prompt(f"Git error: {result.stderr.strip()}")
                sys.exit(1)
            if not result.stdout.strip():
                Prompts.error_prompt(
                    f"Author '{author}' not found in the repository.")
                sys.exit(1)
        except FileNotFoundError:
            Prompts.error_prompt(
                "Git is not installed or not found in PATH."
            )
            sys.exit(1)

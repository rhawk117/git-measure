import argparse
from pathlib import Path
import subprocess
import sys
from collections import defaultdict
from colorama import init, Fore, Style

init(autoreset=True)


def set_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Analyze Git repository contributions by authors.'
    )

    parser.add_argument(
        '-p', '--path',
        required=True,
        type=str,
        help='Path to the Git repository'
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '-a', '--author',
        type=str,
        help='Author name to filter commits'
    )

    group.add_argument(
        '-top', '--top_contributors',
        action='store_true',
        help='Display top 10 contributors'
    )

    parser.add_argument(
        '-by', '--by',
        type=str,
        choices=['i', 'd', 'net'],
        default='net',
        help='Metric to rank top contributors by: -i for insertions, -d for deletions, -net for net contributions (default: net)'
    )

    return parser.parse_args()


def check_git():
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
        sys.stderr.write(
            "Git is not installed or not found in PATH. Please install Git from https://git-scm.com/downloads and ensure it's added to your system's PATH.\n"
        )
        sys.exit(1)


def check_git_path(repo_path: Path):
    git_dir = repo_path / '.git'
    if not git_dir.is_dir():
        sys.stderr.write(f"{Fore.RED}Error: No .git directory found in the specified path: {
                         repo_path}{Style.RESET_ALL}\n")
        sys.exit(1)


def get_contributors(repo_path: Path):
    try:

        result = subprocess.run(
            ['git', 'log', '--pretty=format:%an', '--numstat'],
            cwd=str(repo_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        if result.returncode != 0:
            sys.stderr.write(f"{Fore.RED}Git error: {
                             result.stderr.strip()}{Style.RESET_ALL}\n")
            sys.exit(1)

        contributions = defaultdict(lambda: {'insertions': 0, 'deletions': 0})
        current_author = None

        for line in result.stdout.split('\n'):
            if not line.strip():
                continue
            if '\t' not in line:
                current_author = line.strip()
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
                contributions[current_author]['insertions'] += insert
                contributions[current_author]['deletions'] += delete

        for author in contributions:
            contributions[author]['net'] = contributions[author]['insertions'] - \
                contributions[author]['deletions']

        return contributions
    except FileNotFoundError:
        sys.stderr.write(f"{Fore.RED}Error: Git is not installed or not found in PATH.{
                         Style.RESET_ALL}\n")
        sys.exit(1)


def check_author_exists(repo_path: Path, author: str):
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
            sys.stderr.write(f"{Fore.RED}Git error: {
                             result.stderr.strip()}{Style.RESET_ALL}\n")
            sys.exit(1)
        if not result.stdout.strip():
            sys.stderr.write(f"{Fore.RED}Error: Author '{
                             author}' not found in the repository.{Style.RESET_ALL}\n")
            sys.exit(1)
    except FileNotFoundError:
        sys.stderr.write(f"{Fore.RED}Error: Git is not installed or not found in PATH.{
                         Style.RESET_ALL}\n")
        sys.exit(1)


def get_contribution_stats(repo_path: Path, author: str):
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
            sys.stderr.write(f"{Fore.RED}Git error: {
                             result.stderr.strip()}{Style.RESET_ALL}\n")
            sys.exit(1)

        insertions = deletions = 0

        for line in result.stdout.split('\n'):
            if not line.strip():
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

        net_contribution = insertions - deletions
        return insertions, deletions, net_contribution
    except FileNotFoundError:
        sys.stderr.write(f"{Fore.RED}Error: Git is not installed or not found in PATH.{
                         Style.RESET_ALL}\n")
        sys.exit(1)


def display_author_stats(author: str, insertions: int, deletions: int, net: int):
    headers = [
        f"{Fore.CYAN}Author{Style.RESET_ALL}",
        f"{Fore.GREEN}Insertions{Style.RESET_ALL}",
        f"{Fore.RED}Deletions{Style.RESET_ALL}",
        f"{Fore.YELLOW}Net Contribution{Style.RESET_ALL}"
    ]

    row = [author, f"{insertions:,}", f"{deletions:,}", f"{net:,}"]

    col_widths = [max(len(str(item)) for item in column)
                  for column in zip(headers, row)]

    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])

    print(format_str.format(*headers))
    print("-+-".join(['-' * w for w in col_widths]))

    print(format_str.format(*row))


def display_top_contributors(contributions: dict, by: str):
    sorted_contributors = sorted(
        contributions.items(), key=lambda x: x[1][by], reverse=True)

    top_contributors = sorted_contributors[:10]
    headers = [f"{Fore.CYAN}Rank{Style.RESET_ALL}",
               f"{Fore.CYAN}Author{Style.RESET_ALL}",
               f"{Fore.GREEN}Insertions{Style.RESET_ALL}",
               f"{Fore.RED}Deletions{Style.RESET_ALL}",
               f"{Fore.YELLOW}Net Contribution{Style.RESET_ALL}"]

    col_widths = [10, 25, 15, 15, 20]
    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])
    print(format_str.format(*headers))
    print("-+-".join(['-' * w for w in col_widths]))
    for idx, (author, stats) in enumerate(top_contributors, start=1):
        row = [
            f"{Fore.CYAN}{idx}{Style.RESET_ALL}",
            author,
            f"{Fore.GREEN}{stats['insertions']:,}{Style.RESET_ALL}",
            f"{Fore.RED}{stats['deletions']:,}{Style.RESET_ALL}",
            f"{Fore.YELLOW}{stats['net']:,}{Style.RESET_ALL}"
        ]
        print(format_str.format(*row))


def main():
    args = set_args()
    repo_path = Path(args.path).resolve()
    author = args.author
    top = args.top_contributors
    by = args.by  # 'i', 'd', or 'net'

    check_git()

    check_git_path(repo_path)

    if top:
        contributions = get_contributors(repo_path)

        if not contributions:
            print(f"{Fore.YELLOW}No contributions found in the repository.{
                  Style.RESET_ALL}")
            sys.exit(0)

        metric_map = {
            'i': 'insertions',
            'd': 'deletions',
            'net': 'net'
        }
        metric = metric_map.get(by, 'net')

        print(f"\nTop Contributors Ranked by {metric.capitalize()}:\n")
        display_top_contributors(contributions, metric)
    else:
        check_author_exists(repo_path, author)

        insertions, deletions, net = get_contribution_stats(repo_path, author)

        print()
        display_author_stats(author, insertions, deletions, net)
        print()


if __name__ == '__main__':
    main()

# main.py

import argparse
from pathlib import Path
from git import GitUtils, GitResults, GitData
from display import display_author_stats, display_top_contributors, display_repo_info
from display import Prompts
from colorama import Fore
from app import App
import sys


def set_app_args():
    parser = argparse.ArgumentParser(
        description='Analyze Git repository contributions by authors.'
    )

    parser.add_argument(
        '-p', '--path',
        type=str,
        help='Path to the Git repository'
    )

    group = parser.add_mutually_exclusive_group()

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

    group.add_argument(
        '-i', '--info',
        action='store_true',
        help='Display repository information'
    )

    parser.add_argument(
        '-by', '--by',
        type=str,
        choices=['i', 'd', 'net'],
        default='net',
        help='Metric to rank top contributors by: -i for insertions, -d for deletions, -net for net contributions (default: net)'
    )

    return parser.parse_args()


def run_as_cli(args):
    if not args.path:
        Prompts.error_prompt(
            "Error: The -p/--path argument is required in command-line mode.")
        sys.exit(1)

    repo_path = Path(args.path).resolve()
    author = args.author
    top = args.top_contributors
    info = args.info
    by = args.by  # 'i', 'd', or 'net'

    GitUtils.validate_git(repo_path)

    if info:
        git_data = GitData(repo_path)
        display_repo_info(git_data)
    elif top:
        git_data = GitData(repo_path)
        Prompts.info_prompt(f"Top Contributors Ranked by {by.upper()}:")
        display_top_contributors(
            git_data.git_results.get_top_contributors(by=by), by)
    elif author:
        GitUtils.check_author_exists(repo_path, author)

        git_data = GitData(repo_path)
        display_author_stats(git_data.git_results.get_contribution(author))
    else:
        Prompts.error_prompt(
            "No action specified. Use -a/--author, -top, or -i/--info."
        )
        sys.exit(1)


def main() -> None:
    if len(sys.argv) > 1:
        args = set_app_args()
        run_as_cli(args)
    else:
        app = App()
        app.start()


if __name__ == '__main__':
    main()

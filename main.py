# main.py

import argparse
from pathlib import Path
from git_utils import GitUtils, GitResults
from display import display_author_stats, display_top_contributors
from display import Prompts
from colorama import Fore
from app import App
import sys


def parse_arguments():
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

    parser.add_argument(
        '-by', '--by',
        type=str,
        choices=['i', 'd', 'net'],
        default='net',
        help='Metric to rank top contributors by: -i for insertions, -d for deletions, -net for net contributions (default: net)'
    )

    return parser.parse_args()


def run_command_line_mode(args):
    if not args.path:
        Prompts.error_prompt(
            "Error: The -p/--path argument is required in command-line mode."
        )
        sys.exit(1)

    repo_path = Path(args.path).resolve()
    author = args.author
    top = args.top_contributors
    by = args.by  # 'i', 'd', or 'net'
    GitUtils.validate_git(repo_path)

    if top:
        git_result = GitResults()
        git_output = GitUtils.fetch_git_data(repo_path)
        GitUtils.resolve_git_output(git_output, git_result)
        Prompts.info_prompt(f"Top Contributors Ranked by {by.upper()}:")
        display_top_contributors(git_result.get_top_contributors(by=by), by)
    elif author:
        GitUtils.check_author_exists(repo_path, author)
        git_result = GitResults()
        git_output = GitUtils.fetch_git_data(repo_path, author=author)
        GitUtils.resolve_git_output(git_output, git_result)

        Prompts.color_print("", Fore.RESET)
        display_author_stats(git_result.get_contribution(author))
        Prompts.color_print("", Fore.RESET)


def main():
    if len(sys.argv) > 1:
        args = parse_arguments()
        run_command_line_mode(args)
    else:
        app = App()
        app.start()


if __name__ == '__main__':
    main()

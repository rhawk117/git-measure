# app.py

import shlex
from pathlib import Path
from git_utils import GitUtils, GitResults, AuthorResults
from display import display_author_stats, display_top_contributors
from display import Prompts
from colorama import Fore
from typing import Optional


class App:
    """
    Interactive application for Git Contribution Counter.
    """

    def __init__(self):
        self.repo_path: Optional[Path] = None
        self.git_results = GitResults()

    def start(self):
        Prompts.info_prompt(
            "Welcome to Git Contribution Counter Interactive Shell!")
        Prompts.color_print(
            "Type 'help' to see available commands.\n", Fore.CYAN)
        while True:
            try:
                user_input = input(f"{Fore.BLUE}>>> {Fore.RESET}").strip()
                if not user_input:
                    continue
                command_parts = shlex.split(user_input)
                if not command_parts:
                    continue
                command = command_parts[0].lower()
                args = command_parts[1:]

                match command:
                    case 'exit' | 'quit':
                        Prompts.info_prompt(
                            "Exiting interactive shell. Goodbye!")
                        break
                    case 'help':
                        self.print_help()
                    case 'setpath':
                        self.handle_setpath(args)
                    case 'author':
                        self.handle_author(args)
                    case 'top':
                        self.handle_top(args)
                    case _:
                        Prompts.error_prompt(f"Unknown command: {
                                             command}. Type 'help' to see available commands.")
            except KeyboardInterrupt:
                print()
                Prompts.info_prompt("Exiting interactive shell. Goodbye!")
                break
            except Exception as e:
                Prompts.error_prompt(f"Error: {e}")

    def print_help(self):
        help_text = f"""
{Prompts.color_text(Fore.CYAN, 'Available Commands:')}

- {Prompts.color_text(Fore.YELLOW, 'setpath <path>')}
    Set the path to the Git repository.

- {Prompts.color_text(Fore.YELLOW, 'author "<author_name>"')}
    Display statistics for a specific author.

- {Prompts.color_text(Fore.YELLOW, 'top [-by i|d|net]')}
    Display top 10 contributors.
    Optional flag:
        -by i    Rank by Insertions
        -by d    Rank by Deletions
        -by net  Rank by Net Contribution (default)

- {Prompts.color_text(Fore.YELLOW, 'help')}
    Show this help message.

- {Prompts.color_text(Fore.YELLOW, 'exit / quit')}
    Exit the interactive shell.
"""
        Prompts.color_print(help_text, Fore.CYAN)

    def handle_setpath(self, args):
        if not args:
            Prompts.error_prompt("'setpath' requires a path argument.")
            return
        path = Path(args[0]).resolve()
        if not path.is_dir():
            Prompts.error_prompt(
                f"The path '{path}' does not exist or is not a directory.")
            return
        GitUtils.validate_git(path)
        self.repo_path = path
        self.git_results = GitResults()
        git_output = GitUtils.fetch_git_data(path)
        GitUtils.resolve_git_output(git_output, self.git_results)
        Prompts.success_prompt(f"Git repository set to: {path}")

    def handle_author(self, args):
        if not self.repo_path:
            Prompts.error_prompt(
                "Repository path not set. Use 'setpath <path>' first.")
            return
        if not args:
            Prompts.error_prompt("'author' command requires an author name.")
            return
        author = args[0]
        author_result = self.git_results.get_contribution(author)
        if not author_result:
            # Verify using GitUtils
            try:
                GitUtils.check_author_exists(self.repo_path, author)
                # Refresh git_results to include this author
                self.git_results = GitResults()
                git_output = GitUtils.fetch_git_data(
                    self.repo_path, author=author)
                GitUtils.resolve_git_output(git_output, self.git_results)
                author_result = self.git_results.get_contribution(author)
            except SystemExit:
                return
        display_author_stats(author_result)

    def handle_top(self, args):
        if not self.repo_path:
            Prompts.error_prompt(
                "Repository path not set. Use 'setpath <path>' first.")
            return
        by = 'net'  # default
        if args:
            if len(args) >= 2 and args[0] == '-by':
                if args[1] in ['i', 'd', 'net']:
                    by = args[1]
                else:
                    Prompts.error_prompt(
                        "Invalid flag for 'top' command. Use -by i|d|net.")
                    return
            else:
                Prompts.error_prompt(
                    "Invalid arguments for 'top' command. Use 'top -by i|d|net'.")
                return
        top_contributors = self.git_results.get_top_contributors(by=by)
        display_top_contributors(top_contributors, by)


from colorama import Fore, Style, init
import sys

init(autoreset=True)


class Prompts:
    @staticmethod
    def color_text(fore_color, text: str) -> str:
        return f"{fore_color}{text}{Style.RESET_ALL}"

    @staticmethod
    def color_print(text: str, fore_color):
        print(Prompts.color_text(fore_color, text))

    @staticmethod
    def color_stderr(text: str, fore_color):
        sys.stderr.write(Prompts.color_text(fore_color, text) + "\n")

    @staticmethod
    def info_prompt(message: str):
        formatted_message = f"[i] {message} [i]"
        Prompts.color_print(formatted_message, Fore.GREEN)

    @staticmethod
    def success_prompt(message: str):
        formatted_message = f"[*] {message} [*]"
        Prompts.color_print(formatted_message, Fore.BLUE)

    @staticmethod
    def error_prompt(message: str):
        formatted_message = f"[!] {message} [!]"
        Prompts.color_print(formatted_message, Fore.RED)


def display_author_stats(author_result):
    if not author_result:
        Prompts.color_print(
            "No contributions were found for the specified author.",
            Fore.YELLOW
        )
        return

    headers = [
        Prompts.color_text(Fore.CYAN, "Author"),
        Prompts.color_text(Fore.GREEN, "Commits"),
        Prompts.color_text(Fore.GREEN, "Insertions"),
        Prompts.color_text(Fore.RED, "Deletions"),
        Prompts.color_text(Fore.YELLOW, "Net Contribution")
    ]

    row = [
        author_result.author,
        f"{author_result.commits:,}",
        f"{author_result.insertions:,}",
        f"{author_result.deletions:,}",
        f"{author_result.net:,}"
    ]

    col_widths = [max(len(str(item)) for item in column)
                  for column in zip(headers, row)]

    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])

    Prompts.color_print(format_str.format(*headers), Fore.CYAN)
    Prompts.color_print("-+-".join(['-' * w for w in col_widths]), Fore.CYAN)

    Prompts.color_print(format_str.format(*row), Fore.RESET)


def display_top_contributors(top_contributors: list, by: str):
    if not top_contributors:
        Prompts.color_print(
            "No contributions found in the repository.", Fore.YELLOW)
        return

    headers = [
        Prompts.color_text(Fore.CYAN, "Rank"),
        Prompts.color_text(Fore.CYAN, "Author"),
        Prompts.color_text(Fore.GREEN, "Commits"),
        Prompts.color_text(Fore.GREEN, "Insertions"),
        Prompts.color_text(Fore.RED, "Deletions"),
        Prompts.color_text(Fore.YELLOW, "Net Contribution")
    ]

    col_widths = [5, 25, 10, 15, 15, 20]
    format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])

    Prompts.color_print(format_str.format(*headers), Fore.CYAN)
    Prompts.color_print("-+-".join(['-' * w for w in col_widths]), Fore.CYAN)

    for contributor in top_contributors:
        row = [
            f"{contributor.rank}",
            contributor.author,
            f"{contributor.commits:,}",
            f"{contributor.insertions:,}",
            f"{contributor.deletions:,}",
            f"{contributor.net:,}"
        ]
        Prompts.color_print(format_str.format(*row), Fore.RESET)


def display_repo_info(git_data):
    headers = [
        Prompts.color_text(Fore.CYAN, "Repository Information")
    ]
    Prompts.color_print("\n".join(headers), Fore.CYAN)
    Prompts.color_print("-" * 50, Fore.CYAN)

    info = [
        (Prompts.color_text(Fore.YELLOW, "Repository Path:"), git_data.repo_path),
        (Prompts.color_text(Fore.YELLOW, "Creation Date:"), git_data.creation_date),
        (Prompts.color_text(Fore.YELLOW, "Last Commit Date:"),
         git_data.last_commit_date),
        (Prompts.color_text(Fore.YELLOW, "Branches:"), ", ".join(git_data.branches)),
        (Prompts.color_text(Fore.YELLOW, "Predominant Language:"),
         git_data.predominant_language),
        (Prompts.color_text(Fore.YELLOW, "Authors:"), ", ".join(git_data.authors)),
    ]

    for label, value in info:
        Prompts.color_print(f"{label} {value}", Fore.RESET)

    Prompts.color_print("", Fore.RESET)

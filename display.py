from colorama import Fore, Style, init
import sys

init(autoreset=True)

class Prompts:
    @staticmethod
    def color_text(fore_color, text: str) -> str:
        return f"{fore_color}{text}{Style.RESET_ALL}"

    @staticmethod
    def color_print(text: str, fore_color) -> None:
        print(Prompts.color_text(fore_color, text))

    @staticmethod
    def color_stderr(text: str, fore_color) -> None:
        sys.stderr.write(Prompts.color_text(fore_color, text) + "\n")

    @staticmethod
    def info_prompt(message: str) -> None:
        formatted_message = f"[i] {message} [i]"
        Prompts.color_print(formatted_message, Fore.GREEN)

    @staticmethod
    def success_prompt(message: str) -> None:
        formatted_message = f"[*] {message} [*]"
        Prompts.color_print(formatted_message, Fore.BLUE)

    @staticmethod
    def error_prompt(message: str) -> None:
        formatted_message = f"[!] {message} [!]"
        Prompts.color_print(formatted_message, Fore.RED)


def display_author_stats(author_result) -> None:
    if not author_result:
        Prompts.color_print(
            "No contributions found for the specified author.",
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


def display_top_contributors(top_contributors: list, by: str) -> None:
    if not top_contributors:
        Prompts.color_print(
            "No contributions found in the repository.",
            Fore.YELLOW
        )
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
    table_bars = "-+-".join(['-' * w for w in col_widths])
    Prompts.color_print(format_str.format(*headers), Fore.CYAN)
    Prompts.color_print(table_bars, Fore.CYAN)

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

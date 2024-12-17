from colorama import Fore, Style

def color_text(fore_color, text: str) -> str:
    return f"{fore_color}{text}{Style.RESET_ALL}"

def print_colored(text: str, fore_color) -> None:
    print(color_text(fore_color, text))
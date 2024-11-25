from colorama import Fore, Style

def log_info(message):
    """
    Logs an informational message in blue.

    Parameters:
    - message: The message to log.
    """
    print(f"{Fore.BLUE}[INFO]{Style.RESET_ALL} {message}")


def log_warning(message):
    """
    Logs a warning message in yellow.

    Parameters:
    - message: The message to log.
    """
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")


def log_error(message):
    """
    Logs an error message in red.

    Parameters:
    - message: The message to log.
    """
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

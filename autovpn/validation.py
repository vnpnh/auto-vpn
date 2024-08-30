from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

from autovpn.const import VPNService


def validate_host(host: str) -> bool:
    """
    Validates the host input to ensure it contains a dot and is at least four characters long.

    Args:
        host (str): The host string to validate.

    Returns:
        bool: True if the host is valid, False otherwise.
    """
    return '.' in host and len(host) > 3  # Basic check for a somewhat valid domain or IP

def validate_user(user: str) -> bool:
    """
    Validates the username input to ensure it is not empty.

    Args:
        user (str): The username string to validate.

    Returns:
        bool: True if the username is valid, False otherwise.
    """
    return len(user) > 0  # Basic check to ensure it's not empty

def validate_vpn_type(vpn_type: str) -> bool:
    """
    Validates the VPN type to ensure it is among the supported types.

    Args:
        vpn_type (str): The VPN type string to validate.

    Returns:
        bool: True if the VPN type is valid, False otherwise.
    """
    valid_types = [VPNService.CISCO, VPNService.FORTI]  # Example VPN types
    return vpn_type in valid_types

def get_valid_input(prompt_text: str, error_message: str, validation_func=lambda x: True) -> str:
    """
    Utility function to get and validate user input with a custom validation function.

    Args:
        prompt_text (str): The text to prompt the user for input.
        error_message (str): The error message to display if validation fails.
        validation_func (Callable[[str], bool]): A function to validate the input.

    Returns:
        str: The valid user input.
    """
    while True:
        user_input = Prompt.ask(Text(prompt_text, style="bold magenta"))
        if user_input and validation_func(user_input):
            return user_input.strip()
        else:
            error_details = f"Invalid input: {user_input}" if user_input else "Input cannot be empty."
            full_error_message = f"{error_message} {error_details}"
            Console().print(Text(full_error_message, style="bold red on black"))

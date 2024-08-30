import sys
from typing import NoReturn

from rich.console import Console

from autovpn.cli import VPNCLI
from autovpn.encryption import Encryption
from autovpn.exceptions.exception import VPNError
from autovpn.utils import get_db_filename, secure, load_encryption_key

key = load_encryption_key()
encryption = Encryption(key)
db_path = get_db_filename()


@secure(encryption, db_path)
def run_vpn_cli(path) -> None:
    vpn_cli = VPNCLI(path)
    vpn_cli.run()


def handle_error(error: Exception) -> NoReturn:
    console = Console(color_system="windows")
    if isinstance(error, KeyboardInterrupt):
        console.print("VPN operation terminated by user", style="bold yellow")
        sys.exit(0)
    elif isinstance(error, VPNError):
        console.print(f"VPN Error: {error}", style="bold red")
    else:
        console.print(f"An unexpected error occurred: {error}", style="bold red")
    sys.exit(1)


def main() -> None:
    try:
        run_vpn_cli()
    except Exception as e:
        handle_error(e)


if __name__ == "__main__":
    main()

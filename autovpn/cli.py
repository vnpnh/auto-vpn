import argparse
import configparser
import getpass
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Type, Optional, Callable

from rich.table import Table
from rich.text import Text

from autovpn import utils
from autovpn.manager.cisco import Cisco
from autovpn.manager.forti import Forti
from autovpn.const import VPNConst, VPNService
from autovpn.manager.manager import Manager
from rich.console import Console

from autovpn.manager.sqllite import SQLiteManager
from autovpn.validation import validate_vpn_type, validate_host, validate_user, get_valid_input
from autovpn.version import VERSION_TEXT, DESCRIPTION, AUTHOR, LICENSE


@dataclass
class VPNCLI(SQLiteManager):
    """
    VPN Command Line Interface for managing VPN connections.

    Attributes:
        parser (argparse.ArgumentParser): Command line argument parser.
        args (Optional[argparse.Namespace]): Parsed command line arguments.
        config (configparser.ConfigParser): Configuration file parser.
        vpn_instance (Optional[Manager]): Instance of VPN manager.
        console (Console): Console object for rich text display.
        VPN_CLASSES (Dict[str, Type[Manager]]): Mapping of VPN service names to their respective Manager classes.
    """
    parser: argparse.ArgumentParser = field(init=False)
    args: Optional[argparse.Namespace] = None
    config: configparser.ConfigParser = field(default_factory=configparser.ConfigParser)
    vpn_instance: Optional[Manager] = None
    console: Console = field(init=False)
    data = None

    VPN_CLASSES: Dict[str, Type[Manager]] = field(default_factory=lambda: {
        VPNService.CISCO: Cisco,
        VPNService.FORTI: Forti,
    })

    def __post_init__(self):
        super().__post_init__()
        self.parser = self._create_parser()
        self.args = self.parser.parse_args()
        self.console = Console(color_system='windows')
        self.display_app_info()
        if self.args.set_config and self.args.type:
            self.create_or_update_config()
        if self.args.supported:
            self.console.print("Supported VPN: cisco, forti", style="bold cyan")
            sys.exit(0)

    def display_app_info(self):
        version_text = Text(f"Version: {VERSION_TEXT}", style="bold blue")
        description_text = Text(DESCRIPTION, style="dim")
        author_text = Text(f"Author: {AUTHOR}", style="green")
        license_text = Text(f"License: {LICENSE}", style="red")

        self.display_stylized_ascii_art()
        self.console.print(version_text)
        self.console.print(description_text)
        self.console.print(author_text)
        self.console.print(license_text)
        if not self.args.action:
            self.parser.print_help()

    def display_stylized_ascii_art(self):
        ascii_art = Text(r"""
            ____________  _______________     ___    ______________   __
            ___    |_  / / /__  __/_  __ \    __ |  / /__  __ \__  | / /
            __  /| |  / / /__  /  _  / / /    __ | / /__  /_/ /_   |/ / 
            _  ___ / /_/ / _  /   / /_/ /     __ |/ / _  ____/_  /|  /  
            /_/  |_\____/  /_/    \____/      _____/  /_/     /_/ |_/
        """, style="bold red")
        self.console.print(ascii_art)

    @classmethod
    def _create_parser(cls) -> argparse.ArgumentParser:
        """
        Creates and configures the argument parser with all necessary subparsers and options.

        Returns:
            argparse.ArgumentParser: Configured argument parser.
        """
        parser = argparse.ArgumentParser(description="VPN Management CLI")
        subparsers = parser.add_subparsers(dest="action")
        parser.add_argument("-f", "--force", action="store_true", help="Force create config even if it exists")
        parser.add_argument("-l", "--list", action="store_true", help="List all available configurations")
        parser.add_argument("--config", type=str, help="Name of the configuration to delete or use")
        parser.add_argument("-sc","--set-config", type=str, help="Set the VPN client executable path")
        parser.add_argument("-t","--type", type=str, choices=[VPNService.CISCO, VPNService.FORTI], help="Type of VPN client (e.g., cisco)")
        parser.add_argument("--delete", action="store_true", help="Delete a specific configuration by name")
        parser.add_argument("--supported", action="store_true", help="List supported VPN types")

        connect_parser = subparsers.add_parser(VPNConst.CONNECT, help="Connect to VPN")
        connect_parser.add_argument("vpn_type", choices=[VPNService.CISCO, VPNService.FORTI],
                                    help="Type of VPN (cisco, forti)")
        connect_parser.add_argument("-r", "--retry", type=int, default=3, help="Number of connection retry attempts")
        connect_parser.add_argument("-d", "--delay", type=int, default=5,
                                    help="Delay in seconds between retry attempts")
        connect_parser.add_argument("-C", "--config", help="Use a specific config for connection")
        connect_parser.add_argument("-H", "--host", help="Manually provide host for VPN connection")
        connect_parser.add_argument("-U", "--user", help="Manually provide username for VPN connection")
        connect_parser.add_argument("-P", "--password", help="Manually provide password for VPN connection")
        connect_parser.add_argument("-S", "--save", help="Save manual connection details with a specific config name")
        connect_parser.add_argument("-f", "--force", action="store_true",
                                   help="Force create config even if it exists")
        disconnect_parser = subparsers.add_parser(VPNConst.DISCONNECT, help="Disconnect from VPN")
        disconnect_parser.add_argument("vpn_type", choices=[VPNService.CISCO, VPNService.FORTI],
                                       help="Type of VPN (cisco, forti)")

        status_parser = subparsers.add_parser(VPNConst.STATUS, help="Check VPN connection status")
        status_parser.add_argument("vpn_type", choices=[VPNService.CISCO, VPNService.FORTI],
                                   help="Type of VPN (cisco, forti)")

        create_parser = subparsers.add_parser("create", help="create config file")
        create_parser.add_argument("-f", "--force", action="store_true",
                                     help="Force create config even if it exists")
        create_parser.add_argument("-C", "--config", help="Create a new config with the specified name")

        return parser

    def save_config(self, host: str, user: str, password: str, config_name: str, vpn_type: str) -> None:
        """
        Saves or updates VPN configuration securely.

        Parameters:
           host (str): VPN host.
           user (str): Username for VPN.
           password (str): Password for VPN.
           config_name (str): Configuration profile name.
        """
        match (host, user, password):
            case ('', *_) | (_, '', *_) | (_, _, ''):
                self.console.print("All fields are required. Please provide valid inputs.", style="bold red")
                return

        try:
            existing_data = self.get_config(config_name)
            if existing_data:
                match self.args.force:
                    case True:
                        self.update_config(config_name, host, user, password, vpn_type)
                        self.console.print(f"Existing config '{config_name}' has been overwritten.",
                                           style="bold yellow")
                    case False:
                        self.console.print("Config name already exists. Use -f to overwrite.", style="bold red")
                        return
            else:
                self.insert_config(config_name, host, user, password, vpn_type)
                self.console.print(f"Successfully saved config: {config_name}", style="bold green")
        except configparser.NoSectionError:
            self.console.print("Error: Configuration section missing.", style="bold red")
        except configparser.DuplicateSectionError:
            self.console.print("Error: Duplicate configuration section.", style="bold red")
        except Exception as e:
            self.console.print(f"Failed to save config: {str(e)}", style="bold red")

    def create_or_update_config(self):
        config_file_path = utils.get_config_file()
        config = configparser.ConfigParser()
        config_file = config_file_path
        if config_file.exists():
            config.read(config_file_path)

        if 'path' not in config:
            config['path'] = {}

        config['path'][self.args.type] = self.args.set_config

        with open(config_file_path, 'w') as configfile:
            config.write(configfile)

        if config_file.exists():
            self.console.print(f"Updated {self.args.type} path to {self.args.set_config}", style="bold green")
        else:
            self.console.print(f"Created configuration file and set {self.args.type} path to {self.args.set_config}", style="bold green")

    def load_config(self) -> None:
        config_file = utils.get_config_file()

        if not config_file.is_file():
            self.console.print(f"Config file not found: {config_file}", style="bold red")
            sys.exit(1)

        self.config.read(config_file)

        if 'path' not in self.config:
            self.console.print("Config path section not found", style="bold red")
            sys.exit(1)

        if self.args.action == VPNConst.CONNECT:
            if all(hasattr(self.args, attr) and getattr(self.args, attr) for attr in ['host', 'user', 'password']):
                self.data = {
                    'config_name': self.args.config,
                    'host': self.args.host,
                    'username': self.args.user,
                    'password': self.args.password,
                }
                if getattr(self.args, 'save', None):
                    config_name = self.args.save
                    self.save_config(self.args.host, self.args.user, self.args.password, config_name, self.args.vpn_type)
            else :
                self.data = self.get_config(self.args.config)
                if not self.data and not self.args.host:
                    self.console.print(f"Config not found!", style="bold red")
                    sys.exit(1)

    def set_config(self):
        pass

    def get_vpn_paths(self) -> Path:
        config_path = self.config.get('path', self.args.vpn_type, fallback=None)
        if not config_path:
            self.console.print("VPN path not found in config", style="bold red")
            sys.exit(1)

        return Path(config_path)

    def create_new_config(self):
        config_name = self.args.config
        host = self.args.host
        username = self.args.user
        password = self.args.password
        vpn_type = self.args.vpn_type

        if not all([config_name, host, username, password, vpn_type]):
            self.console.print("Please provide all required arguments for creating a new config.", style="bold red")
            self.parser.print_help()
            sys.exit(1)

        existing_config = self.get_config(config_name)
        if existing_config:
            self.console.print(f"Config '{config_name}' already exists.", style="bold red")
            sys.exit(1)

        self.insert_config(config_name, host, username, password, vpn_type)
        self.console.print(f"New config '{config_name}' created successfully.", style="bold green")

    def initialize_vpn(self) -> None:
        if not hasattr(self.args, 'vpn_type') or self.args.vpn_type not in self.VPN_CLASSES:
            self.console.print("Invalid or missing VPN type. Use 'cisco' or 'forti'.", style="bold red")
            self.parser.print_help()
            sys.exit(1)
        self.load_config()
        config_path = self.get_vpn_paths()
        vpn_class = self.VPN_CLASSES[self.args.vpn_type]

        self.vpn_instance = vpn_class(path=config_path, console=self.console)
        if self.data:
            self.vpn_instance = vpn_class(host=self.data['host'], username=self.data['username'],
                                          password=self.data['password'], path=config_path,
                                          console=self.console)


    def handle_vpn_actions(self):
        if hasattr(self.args, 'retry') and self.args.retry is not None:
            self.vpn_instance.settings.retries = self.args.retry
        if hasattr(self.args, 'delay') and self.args.delay is not None:
            self.vpn_instance.settings.delay = max(self.args.delay, 0)
        actions: Dict[str, Callable[[], None]] = {
            VPNConst.CONNECT: lambda: self.vpn_instance.connect() if self.vpn_instance else None,
            VPNConst.DISCONNECT: lambda: self.vpn_instance.disconnect() if self.vpn_instance else None,
            VPNConst.STATUS: lambda: self.vpn_instance.status() if self.vpn_instance else None,
        }

        action_func = actions.get(self.args.action)
        if action_func:
            action_func()
        else:
            self.console.print(f"Invalid action: {self.args.action}", style="bold red")
            self.parser.print_help()
            sys.exit(1)

    def handle_list_configs(self) -> None:
        """
        Handles the --list action to display VPN configurations.
        """
        table = Table(title="VPN Configurations")
        table.add_column("Config Name", style="cyan", no_wrap=True)
        table.add_column("Host", style="magenta")
        table.add_column("Username", style="green")
        table.add_column("VPN Type", style="bold blue")
        table.add_column("Created At", style="dim")
        table.add_column("Updated At", style="dim")

        if self.args.type:
            configs = self.get_config_by_type(self.args.type)
            if not configs:
                self.console.print(f"No configurations found for VPN type: {self.args.type}", style="bold red")
            else:
                for config in configs:
                    table.add_row(
                        config['config_name'],
                        config['host'],
                        config['username'],
                        config['vpn_type'],
                        config['created_at'],
                        config['updated_at']
                    )
        else:
            configs = self.get_all_configs()
            if not configs:
                self.console.print("No configurations found.", style="bold red")
            else:
                for config in configs:
                    table.add_row(
                        config['config_name'],
                        config['host'],
                        config['username'],
                        config['vpn_type'],
                        config['created_at'],
                        config['updated_at']
                    )

        self.console.print(table)

    def handle_delete_config(self) -> None:
        """
        Handles the --delete action to delete a specific VPN configuration.
        """
        if self.args.config:
            self.delete_config(self.args.config)
            self.console.print(f"Configuration '{self.args.config}' deleted successfully.", style="bold green")
        else:
            self.console.print("Please provide a config name to delete.", style="bold red")

    def run(self) -> None:
        """
        Main entry point for handling command line arguments and initiating VPN actions.
        """
        if self.args.list:
            self.handle_list_configs()
            return

        if self.args.delete:
            self.handle_delete_config()
            return

        if self.args.action == "create" and self.args.config:
            self.console.print("Enter the following details for the new config:")
            vpn_type = get_valid_input(
                "VPN type",
                "Please enter a valid VPN type (e.g., cisco, forti).",
                validate_vpn_type
            )
            host = get_valid_input("Host", "Please enter a valid host.", validate_host)
            user = get_valid_input("User", "User cannot be empty.", validate_user)
            password = getpass.getpass("Password: ").strip()
            self.save_config(host, user, password, self.args.config, vpn_type)

        if self.args.action in [VPNConst.CONNECT, VPNConst.DISCONNECT, VPNConst.STATUS]:
            self.initialize_vpn()
            self.handle_vpn_actions()

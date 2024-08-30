import subprocess
from pathlib import Path
from time import sleep
from dataclasses import dataclass, field
from typing import List, Optional

from rich.progress import Progress

from autovpn.const import VPNConst
from autovpn.network import Network
from autovpn.utils import replace


@dataclass
class Cisco(Network):
    """
    Class for managing Cisco VPN connections.

    Attributes:
        host (Optional[str]): The VPN host.
        username (Optional[str]): The username for VPN connection.
        password (Optional[str]): The password for VPN connection.
        path (Path): The filesystem path to the VPN client executable.
        console (Console): Console object for rich text display.
        credentials (Optional[str]): The credentials string for the connection.
        connect_command (Optional[str]): The command to connect to the VPN.
    """
    credentials: Optional[str] = None
    connect_command: Optional[str] = None
    path: Path = field(init=False)
    console: any = field(init=False)

    def __init__(self,path: Path, console: any, host:str=None, username:str=None, password:str=None):
        super().__init__()
        self.host=host
        self.username = username
        self.password = password
        self.path = path
        self.console = console

    def __post_init__(self):
        super().__post_init__()
        self.connect_command = f"{self.path} -s connect {self.host}"
        self.credentials = f"{self.username}\n{self.password}\ny"

    def open(self) -> None:
        """
        Opens the Cisco AnyConnect application.
        """
        try:
            subprocess.Popen(replace(str(self.path), VPNConst.VPNCLI, VPNConst.VPNUI))
            self.console.print("Cisco AnyConnect application opened successfully.")
        except Exception as e:
            self.console.print(f"Failed to open Cisco AnyConnect application: {e}", style="bold red")

    def terminate(self) -> None:
        """
        Terminates the Cisco AnyConnect application process.
        """
        try:
            subprocess.run(["taskkill", "/F", "/IM", VPNConst.VPNUI], capture_output=True, text=True, check=True)
            self.console.print("Cisco AnyConnect application terminated successfully.")
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to terminate process: {e.stderr}", style="bold red")

    def connect(self) -> None:
        """
        Connects to the VPN, retrying connection attempts upon failure.
        """
        retries = self.settings.retries
        delay = self.settings.delay
        command: List[str] = [self.path, "-s"]

        if self.status():
            self.console.print("VPN is already connected.", style="bold yellow")
            return

        with Progress() as progress:
            task = progress.add_task("[cyan]Connecting to VPN...", total=retries)
            for attempt in range(retries):
                if not self.is_network_ready():
                    self.console.print(f"Network is not ready. Retrying ({attempt + 1}/{retries})...", style="bold yellow")
                    sleep(delay)
                    continue

                try:
                    success_keywords = ["Connected"]
                    self.set_config(self.host, self.username, self.password)
                    process = subprocess.Popen(self.connect_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate(input=self.credentials)
                    if self.status():
                        self.console.print("VPN connected successfully.", style="bold green")
                        progress.update(task, completed=retries)
                        return
                    else:
                        self.console.print(stderr, style="bold red")
                        raise subprocess.CalledProcessError(process.returncode, self.connect_command, output=stdout, stderr=stderr)
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
                    self.console.print(f"Failed to connect to VPN", style="bold red")
                    if attempt < retries - 1:
                        self.console.print(f"Retrying in {delay} seconds...", style="bold yellow")
                        sleep(delay)
                    else:
                        self.console.print("VPN connection attempts failed after multiple retries.", style="bold red")

    def disconnect(self) -> None:
        """
        Disconnects from the VPN.
        """
        command: List[str] = [self.path, VPNConst.DISCONNECT]
        with Progress() as progress:
            task = progress.add_task("[red]Disconnecting to VPN...", total=1)
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                progress.update(task, completed=1)
            except subprocess.CalledProcessError as e:
                self.console.print(f"Failed to disconnect from VPN: {e.stderr}", style="bold red")

    def status(self) -> bool:
        """
        Checks the status of the VPN connection.
        """
        command: List[str] = [self.path, VPNConst.STATE]
        try:
            result = subprocess.run(command, text=True, capture_output=True, check=True)
            output = result.stdout.strip()
            self.console.print(f"VPN Status: {output}")
            return "Connected" in output
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to check VPN status: {e.stderr}", style="bold red")
            return False

    def set_config(self, host: str, username: str, password: str) -> None:
        """
        Sets the VPN configuration including host, username, and password.
        """
        if not self.path:
            raise ValueError("VPN path does not exist.")
        self.connect_command = f"{self.path} -s connect {host}"
        self.credentials = f"{username}\n{password}\ny"

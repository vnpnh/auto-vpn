import subprocess
from time import sleep
from dataclasses import dataclass
from typing import List

from autovpn.const import VPNConst
from autovpn.network import Network
from autovpn.utils import replace


@dataclass
class Forti(Network):
    def __init__(self, path, credential_path, console):
        super().__init__()
        self.path = path
        self.credential_path = credential_path
        self.console = console

    def open(self) -> None:
        """
        Opens the FortiClient application.
        """
        try:
            subprocess.Popen([str(self.path), 'FortiClient.exe'])
            self.console.print("FortiClient application opened successfully.")
        except Exception as e:
            self.console.print(f"Failed to open FortiClient application: {e}", style="bold red")

    def terminate(self) -> None:
        """
        Terminates the FortiClient application process.
        """
        try:
            subprocess.run(["taskkill", "/F", "/IM", "FortiClient.exe"], capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to terminate process: {e.stderr}", style="bold red")

    def connect(self, retries: int = 3, delay: int = 5) -> None:
        """
        Connects to the VPN, retrying connection attempts upon failure.
        """
        command: List[str] = [str(self.path), "-s"]

        if self.status():
            self.console.print("VPN is already connected.", style="bold yellow")
            return

        self.terminate()

        for attempt in range(retries):
            if not self.is_network_ready():
                self.console.print(f"Network is not ready. Retrying ({attempt + 1})...", style="bold yellow")
                sleep(delay)
                continue

            try:
                self.console.print("Connecting to Forti VPN...", style="bold")
                with open(self.credential_path, 'r') as credential_file:
                    result = subprocess.run(
                        command, stdin=credential_file, text=True, capture_output=True, check=True, timeout=30
                    )
                self.console.print(result.stdout)
                self.console.print("VPN connected successfully.", style="bold green")
                return
            except subprocess.TimeoutExpired:
                self.console.print("VPN connection attempt timed out.", style="bold red")
            except subprocess.CalledProcessError as e:
                self.console.print(f"Failed to connect to VPN: {e.stderr}", style="bold red")
                if attempt < retries - 1:
                    self.console.print(f"Retrying in {delay} seconds...", style="bold yellow")
                    self.open()
                    sleep(delay)

        self.console.print("VPN connection attempts failed.", style="bold red")

    def disconnect(self) -> None:
        """
        Disconnects from the VPN.
        """
        command: List[str] = [str(self.path), VPNConst.DISCONNECT]
        try:
            self.console.print("Disconnecting from VPN...", style="bold")
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.console.print("Disconnected from VPN.", style="bold green")
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to disconnect from VPN: {e.stderr}", style="bold red")

    def status(self) -> bool:
        """
        Checks the status of the VPN connection.
        """
        command: List[str] = [str(self.path), VPNConst.STATE]
        try:
            result = subprocess.run(command, text=True, capture_output=True, check=True)
            output = result.stdout.strip()
            self.console.print(f"VPN Status: {output}")
            return "Connected" in output
        except subprocess.CalledProcessError as e:
            self.console.print(f"Failed to check VPN status: {e.stderr}", style="bold red")
            return False

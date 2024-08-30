import subprocess

from autovpn.base import Base
from autovpn.const import SystemOperation


class Network(Base):
    """
    Base class for managing network-related operations.

    Attributes:
       host (Optional[str]): The VPN host.
       username (Optional[str]): The username for VPN connection.
       password (Optional[str]): The password for VPN connection.
    """
    host: str = None
    username: str = None
    password: str = None

    def is_network_ready(self) -> bool:
        """
        Checks if the network is ready by pinging a reliable server (Google DNS).
        Returns:
            bool: True if the network is ready, False otherwise.
        """
        ping_command = "ping"
        ping_count = "-n" if self.system == SystemOperation.WINDOWS else "-c"
        ping_target = "8.8.8.8"

        try:
            subprocess.run(
                [ping_command, ping_count, "1", ping_target],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def connect(self) -> None:
        raise NotImplementedError("Connect method needs to be implemented by subclass.")

    def disconnect(self) -> None:
        raise NotImplementedError("Disconnect method needs to be implemented by subclass.")

    def status(self) -> str:
        raise NotImplementedError("Status method needs to be implemented by subclass.")

    def terminate(self) -> None:
        raise NotImplementedError("Terminate app method needs to be implemented by subclass.")

    def set_config(self, host: str, username: str, password: str) -> None:
        pass

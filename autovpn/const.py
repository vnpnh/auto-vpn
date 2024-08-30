from dataclasses import dataclass


@dataclass
class VPNConst:
    """
    Constants for VPN applications.
    """
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    STATUS = "status"
    STATE = "state"
    VPNUI = "vpnui.exe"
    VPNCLI = "vpncli.exe"


@dataclass
class VPNService:
    CISCO = "cisco"
    FORTI = "forti"

    def is_valid(self, service: str) -> bool:
        return service in [self.CISCO, self.FORTI]


@dataclass
class SystemOperation:
    """
    Constants for system operations.
    """
    WINDOWS = "Windows"
    MACOS = "macOS"
    LINUX = "Linux"
    UNKNOWN = "Unknown"

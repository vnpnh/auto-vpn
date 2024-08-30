from dataclasses import dataclass, field
from pathlib import Path
import sys
from typing import Optional

from autovpn.const import SystemOperation
from autovpn.settings import Settings


@dataclass
class Base:
    """
    Base class providing common attributes and methods.

    Attributes:
        path (Path): Filesystem path to the executable or configuration file.
        settings (Settings): Configuration settings object.
        system (str): Operating system detected at runtime.
    """
    path: Path = field(default_factory=Path)
    settings: Optional[Settings] = field(default_factory=Settings)
    system: str = field(init=False)

    def __post_init__(self):
        """
        Post-initialization to set up the system attribute based on the OS.
        """
        self.system = self.detect_operating_system()

    def detect_operating_system(self) -> str:
        """
        Detects the operating system and updates settings accordingly.

        Returns:
            str: A string representing the detected operating system.
        """
        platform = sys.platform

        if platform.startswith("win"):
            return self._configure_for_windows()
        elif platform.startswith("darwin"):
            return self._configure_for_mac()
        elif platform.startswith("linux"):
            return self._configure_for_linux()
        else:
            return self._handle_unknown_os()

    def _configure_for_windows(self) -> str:
        """
        Configures settings specific to Windows.

        Returns:
            str: The system operation type for Windows.
        """
        return SystemOperation.WINDOWS

    def _configure_for_mac(self) -> str:
        """
        Configures settings specific to macOS.

        Returns:
            str: The system operation type for macOS.
        """
        self.settings.color_system = "auto"
        return SystemOperation.MACOS

    def _configure_for_linux(self) -> str:
        """
        Configures settings specific to Linux.

        Returns:
            str: The system operation type for Linux.
        """
        self.settings.color_system = "auto"
        return SystemOperation.LINUX

    def _handle_unknown_os(self) -> str:
        """
        Handles unknown operating systems.

        Returns:
            str: The system operation type for unknown systems.
        """
        return SystemOperation.UNKNOWN

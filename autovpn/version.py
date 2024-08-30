from typing import Literal, NamedTuple


class VersionInfo(NamedTuple):
    """
    A named tuple to store version information.
    """
    major: int
    minor: int
    patch: int
    release_level: Literal["alpha", "beta", "candidate", "final"]
    serial: int


version = VersionInfo(1, 0, 0, 'beta', 1)


def get_version_text(version_info: VersionInfo) -> str:
    """
    Get the version text for the application.
    """
    if version_info.release_level != 'final' and version_info.serial:
        return (f"{version_info.major}.{version_info.minor}."
                f"{version_info.patch}-{version_info.release_level}{version_info.serial}")
    return f"{version_info.major}.{version_info.minor}.{version_info.patch}"


TITLE = 'AUTO VPN'
DESCRIPTION = ('A simple VPN management tool to connect to a VPN network using a command-line interface.')
AUTHOR = 'vnpnh'
VERSION_TEXT = get_version_text(version)
VERSION_EXTRA = ''
LICENSE = 'MIT License'
COPYRIGHT = 'Copyright 2022-present'

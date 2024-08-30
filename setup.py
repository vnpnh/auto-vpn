from xml.etree.ElementTree import VERSION

from cx_Freeze import setup, Executable
import sys
import os

from autovpn.version import TITLE, DESCRIPTION


build_exe_options = {
    "packages": ["os", "sys", "rich", "cryptography"],
    "excludes": ["tkinter", "PyQt5"],
    "optimize": 2
}

base = None
current_directory = os.getcwd()
icon_path = os.path.join(current_directory, "favicon.ico")

executables = [
    Executable(
        "vpn.py",
        base=base,
        target_name="autovpn.exe",
        icon=icon_path
    )
]


setup(
    name=TITLE,
    version=VERSION,
    description=DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=executables
)

import uuid
from functools import wraps
from pathlib import Path

from cryptography.fernet import Fernet

NAMESPACE = uuid.uuid4()

def get_db_filename() -> Path:
    current_directory = Path.cwd()
    return current_directory / 'vpn_config.db'


def get_config_file() -> Path:
    current_directory = Path.cwd()
    return current_directory / 'config.ini'

def replace(path: str, old: str, new: str) -> str:
    """
    Replace a substring in the given path.

    Args:
        path (str): The original path.
        old (str): The substring to be replaced.
        new (str): The substring to replace with.

    Returns:
        str: The updated path with the substring replaced.
    """
    return path.replace(old, new)


def generate_uuid5(name) -> hex:
    """
    Generate a UUID5 hash from the given name.
    """
    return uuid.uuid5(NAMESPACE, name).hex


def secure(encryption, db_path):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if is_file_exists(db_path):
                encryption.decrypt_file(db_path)
            try:
                result = func(db_path, *args, **kwargs)
            finally:
                encryption.encrypt_file(db_path)
            return result
        return wrapper
    return decorator

def load_encryption_key():
    """Loads or generates an encryption key."""
    key = ""
    key_file = Path("secret.key")
    if key_file.exists():
        with open(key_file, "rb") as file:
            key = file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file:
            file.write(key)
        print(f"New encryption key generated and saved to '{key_file}'.")
    return key

def is_file_exists(file_path: str) -> bool:
    """
    Ensures that the specified file exists.
    If the file does not exist, it creates an empty file.

    Parameters:
    - file_path (str): The path of the file to check or create.

    Returns:
    - bool: True if the file exists or was created successfully, False otherwise.
    """
    file = Path(file_path)
    if file.exists():
        return True

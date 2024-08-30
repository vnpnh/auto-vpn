from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken


class Encryption:
    """Class for managing encryption and decryption using Fernet symmetric encryption."""

    def __init__(self, key: bytes):
        """Initializes the encryption manager with the given encryption key."""
        self.fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts the given plaintext string.

        Args:
            plaintext (str): The string to encrypt.

        Returns:
            str: The encrypted string.
        """
        encrypted = self.fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts the given ciphertext string.

        Args:
            ciphertext (str): The string to decrypt.

        Returns:
            str: The decrypted string.
        """
        decrypted = self.fernet.decrypt(ciphertext.encode())
        return decrypted.decode()

    def encrypt_file(self, input_file_path: Path) -> None:
        """Encrypts a file and saves the encrypted data to the same file.

        Args:
            input_file_path (Path): The path to the input file to encrypt.
        """
        with open(input_file_path, 'rb') as file:
            file_data = file.read()

        encrypted_data = self.fernet.encrypt(file_data)

        with open(input_file_path, 'wb') as file:
            file.write(encrypted_data)

    def decrypt_file(self, input_file_path: Path) -> None:
        """Decrypts a file and saves the decrypted data to the same file.

        Args:
            input_file_path (Path): The path to the encrypted file to decrypt.
        """
        with open(input_file_path, 'rb') as file:
            encrypted_data = file.read()

        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
        except Exception as e:
            return

        with open(input_file_path, 'wb') as file:
            file.write(decrypted_data)

    def is_encrypted(self, file_path: Path) -> bool:
        """Checks if the file is encrypted by attempting to decrypt it.

        Args:
            file_path (Path): The path to the file to check.

        Returns:
            bool: True if the file is encrypted, False otherwise.
        """
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # Try to decrypt the data
            self.fernet.decrypt(file_data)
            return True
        except InvalidToken:
            return False
        except Exception as e:
            print(f"Error while checking encryption: {e}")
            return False
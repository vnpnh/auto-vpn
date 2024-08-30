from dataclasses import dataclass, field
import sqlite3
from pathlib import Path
from datetime import datetime

from autovpn.utils import generate_uuid5


@dataclass
class SQLiteManager:
    """Class for managing a SQLite database for VPN configurations.

    Attributes:
        db_path (Path): The filesystem path to the SQLite database file.
        conn (sqlite3.Connection): SQLite connection object, initialized post-instantiation.
    """
    db_path: Path
    conn: sqlite3.Connection = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Initializes the database connection and creates the vpn_config table if it does not exist."""

        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def setup(self):
        """
        Creates a configuration table if it does not already exist, to store computer-specific information
        and a master password used for encryption. The table includes fields for ID, computer metadata,
        encrypted master password, and timestamps for record creation and updates.
        """
        query = '''
           CREATE TABLE IF NOT EXISTS config (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               computer_info TEXT NOT NULL,
               password TEXT NOT NULL,
               created_at DATETIME DEFAULT (DATETIME('now')),
               updated_at DATETIME DEFAULT (DATETIME('now'))
           );
           '''
        self.conn.execute(query)
        self.conn.commit()

    def create_table(self) -> None:
        """Creates a table for storing VPN configuration if it doesn't already exist."""
        query = '''
        CREATE TABLE IF NOT EXISTS vpn_config (
            id TEXT PRIMARY KEY,
            config_name TEXT NOT NULL UNIQUE,
            host TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            vpn_type TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.conn.execute(query)
        self.conn.commit()

    def insert_config(self, config_name: str, host: str, username: str, password: str, vpn_type: str) -> None:
        """
        Inserts a new VPN configuration into the database.

        Args:
            config_name (str): The name of the VPN configuration.
            host (str): The VPN host.
            username (str): The username for the VPN.
            password (str): The password for the VPN.
            vpn_type (str): The type of VPN.

        Raises:
            ValueError: If the database connection is not initialized.
        """
        if self.conn is None:
            raise ValueError("Database connection is not initialized.")

        try:
            query = '''
            INSERT INTO vpn_config (id, config_name, host, username, password, vpn_type)
            VALUES (?, ?, ?, ?, ?, ?);
            '''
            config_id = generate_uuid5(config_name)
            self.conn.execute(query, (config_id, config_name, host, username, password, vpn_type))
            self.conn.commit()
            print(f"Configuration '{config_name}' saved successfully.")
        except Exception as e:
            print(f"An error occurred while saving the configuration: {e}")
            raise

    def update_config(self, config_name: str, host: str, username: str, password: str, vpn_type: str) -> None:
        """Updates an existing VPN configuration based on the configuration name.

        Args:
            config_name (str): The name of the VPN configuration to update.
            host (str): The new host value.
            username (str): The new username value.
            password (str): The new password value.
            vpn_type (str): The new type of VPN.
        """
        query = '''
        UPDATE vpn_config
        SET host = ?, username = ?, password = ?, vpn_type = ?, updated_at = ?
        WHERE config_name = ?;
        '''
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(query, (host, username, password, vpn_type, updated_at, config_name))
        self.conn.commit()

    def get_all_configs(self) -> list:
        """Retrieves all VPN configurations from the database.

        Returns:
            list: A list of dictionaries containing the VPN configuration details.
        """
        query = '''
        SELECT * FROM vpn_config;
        '''
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        return [{
            'id': row[0],
            'config_name': row[1],
            'host': row[2],
            'username': row[3],
            'password': row[4],
            'vpn_type': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        } for row in rows]

    def get_config_by_type(self, vpn_type: str) -> list:
        """Retrieves a list of VPN configurations by their type.

        Args:
            vpn_type (str): The type of the VPN configurations to retrieve.

        Returns:
            list: A list of dictionaries containing the VPN configuration details.
        """
        query = '''
        SELECT * FROM vpn_config WHERE vpn_type = ?;
        '''
        cursor = self.conn.execute(query, (vpn_type,))
        rows = cursor.fetchall()
        return [{
            'id': row[0],
            'config_name': row[1],
            'host': row[2],
            'username': row[3],
            'password': row[4],
            'vpn_type': row[5],
            'created_at': row[6],
            'updated_at': row[7]
        } for row in rows]

    def get_config(self, config_name: str) -> dict:
        """Retrieves a VPN configuration by its name.

        Args:
            config_name (str): The name of the VPN configuration to retrieve.

        Returns:
            dict: A dictionary containing the VPN configuration details, or None if not found.
        """
        query = '''
        SELECT * FROM vpn_config WHERE config_name = ?;
        '''
        cursor = self.conn.execute(query, (config_name,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'config_name': row[1],
                'host': row[2],
                'username': row[3],
                'password': row[4],
                'vpn_type': row[5],
                'created_at': row[6],
                'updated_at': row[7]
            }
        return None

    def delete_config(self, config_name: str) -> None:
        """Deletes a VPN configuration by its name.

        Args:
            config_name (str): The name of the VPN configuration to delete.
        """
        query = '''
        DELETE FROM vpn_config WHERE config_name = ?;
        '''
        self.conn.execute(query, (config_name,))
        self.conn.commit()

    def close(self) -> None:
        """Closes the database connection."""
        if self.conn:
            self.conn.close()

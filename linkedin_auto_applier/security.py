## security.py

from typing import Dict
from cryptography.fernet import Fernet
import json

class Security:
    """Provides methods for encrypting and decrypting user data to ensure security."""

    def __init__(self, encryption_key: bytes = None):
        """Initializes the Security class with an encryption key.

        Args:
            encryption_key (bytes): The key used for encryption and decryption. If not provided, a new key is generated.
        """
        if encryption_key is None:
            self.encryption_key = Fernet.generate_key()
        else:
            self.encryption_key = encryption_key
        self.cipher = Fernet(self.encryption_key)

    def encrypt_data(self, data: Dict) -> Dict:
        """Encrypts the given data using the encryption key.

        Args:
            data (Dict): The data to be encrypted.

        Returns:
            Dict: A dictionary containing the encrypted data.
        """
        try:
            # Serialize the dictionary to a JSON formatted string and then to bytes
            data_str = json.dumps(data)
            encrypted_data = self.cipher.encrypt(data_str.encode('utf-8'))
            return {"encrypted_data": encrypted_data.decode('utf-8')}
        except Exception as e:
            print(f'Failed to encrypt data: {e}')
            return {"encrypted_data": ""}

    def decrypt_data(self, data: Dict) -> Dict:
        """Decrypts the given data using the encryption key.

        Args:
            data (Dict): The data to be decrypted.

        Returns:
            Dict: A dictionary containing the decrypted data.
        """
        try:
            # Extract the encrypted data and convert it to bytes
            encrypted_data = data.get("encrypted_data", "").encode('utf-8')
            decrypted_data = self.cipher.decrypt(encrypted_data)
            # Convert bytes back to a dictionary using JSON deserialization
            decrypted_data_dict = json.loads(decrypted_data.decode('utf-8'))
            return decrypted_data_dict
        except Exception as e:
            print(f'Failed to decrypt data: {e}')
            return {}

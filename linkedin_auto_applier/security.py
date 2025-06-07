## security.py

import logging
import json # For robust serialization/deserialization
from typing import Dict, Any
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

class Security:
    """Provides methods for encrypting and decrypting data using Fernet."""

    def __init__(self, encryption_key: bytes):
        """Initializes the Security class with a mandatory encryption key.

        Args:
            encryption_key (bytes): The key used for encryption and decryption.
                                    Must be a valid Fernet key.

        Raises:
            ValueError: If encryption_key is not provided or is invalid.
        """
        if not encryption_key:
            logger.error("Encryption key must be provided.")
            raise ValueError("Encryption key must be provided.")

        try:
            self.cipher = Fernet(encryption_key)
            self.encryption_key = encryption_key # Store for potential reference, though cipher uses it
            logger.info("Security class initialized successfully with encryption key.")
        except Exception as e: # Fernet can raise error for invalid key format/type
            logger.error(f"Failed to initialize Fernet cipher with the provided key: {e}", exc_info=True)
            raise ValueError(f"Invalid encryption key provided: {e}")

    def encrypt_data(self, data: Dict[str, Any]) -> str:
        """Encrypts the given dictionary using the encryption key.

        Args:
            data (Dict[str, Any]): The dictionary to be encrypted.

        Returns:
            str: The encrypted data as a string (Fernet token).

        Raises:
            TypeError: If data is not a dictionary.
            Exception: For other encryption failures.
        """
        if not isinstance(data, dict):
            logger.error("Data to encrypt must be a dictionary.")
            raise TypeError("Data to encrypt must be a dictionary.")

        try:
            json_data = json.dumps(data)
            encrypted_bytes = self.cipher.encrypt(json_data.encode('utf-8'))
            encrypted_string = encrypted_bytes.decode('utf-8') # Fernet token is URL-safe base64
            logger.debug("Data encrypted successfully.")
            return encrypted_string
        except TypeError as e: # Changed from json.JSONEncodeError
            # This handles cases where data is not JSON serializable (e.g. set)
            logger.error(f"Failed to serialize data to JSON for encryption (TypeError): {e}", exc_info=True)
            raise # Re-raise to indicate serialization failure
        except Exception as e:
            logger.error(f'Failed to encrypt data: {e}', exc_info=True)
            raise # Re-raise to indicate encryption failure

    def decrypt_data(self, encrypted_string: str) -> Dict[str, Any]:
        """Decrypts the given encrypted string (Fernet token) back into a dictionary.

        Args:
            encrypted_string (str): The encrypted data string (Fernet token).

        Returns:
            Dict[str, Any]: The decrypted dictionary.

        Raises:
            TypeError: If encrypted_string is not a string.
            InvalidToken: If the token is invalid or cannot be decrypted (e.g., wrong key, corrupted).
            Exception: For other decryption or deserialization failures.
        """
        if not isinstance(encrypted_string, str):
            logger.error("Encrypted data to decrypt must be a string.")
            raise TypeError("Encrypted data to decrypt must be a string.")

        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_string.encode('utf-8'))
            json_data = decrypted_bytes.decode('utf-8')
            decrypted_dict = json.loads(json_data)
            logger.debug("Data decrypted successfully.")
            return decrypted_dict
        except InvalidToken as e: # Specific exception for Fernet decryption issues
            logger.error(f"Invalid token or decryption failed (e.g., wrong key, corrupted data): {e}", exc_info=True)
            raise # Re-raise InvalidToken
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize JSON data after decryption: {e}", exc_info=True)
            raise # Re-raise to indicate deserialization failure
        except Exception as e:
            logger.error(f'Failed to decrypt data: {e}', exc_info=True)
            raise # Re-raise for other unexpected errors

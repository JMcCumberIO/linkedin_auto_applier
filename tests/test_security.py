import unittest
import json
from cryptography.fernet import Fernet, InvalidToken
from linkedin_auto_applier.security import Security # Adjust import path if necessary

class TestSecurity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate a valid Fernet key for use in tests
        cls.valid_key = Fernet.generate_key()
        # An intentionally invalid key (e.g., not base64, wrong length for Fernet)
        cls.invalid_key_format = b"this_is_not_a_valid_fernet_key"
        # A different valid key to test decryption failure with wrong key
        cls.different_valid_key = Fernet.generate_key()

    def test_init_successful(self):
        """Test successful initialization with a valid key."""
        try:
            Security(self.valid_key)
        except ValueError:
            self.fail("Security initialization failed with a valid key.")

    def test_init_no_key(self):
        """Test ValueError if encryption_key is not provided."""
        with self.assertRaisesRegex(ValueError, "Encryption key must be provided."):
            Security(None)
        with self.assertRaisesRegex(ValueError, "Encryption key must be provided."):
            Security(b"")

    def test_init_invalid_key_format(self):
        """Test ValueError if encryption_key is invalid (e.g., wrong format/length)."""
        with self.assertRaisesRegex(ValueError, "Invalid encryption key provided"):
            Security(self.invalid_key_format)

    def test_encrypt_data_successful(self):
        """Test successful encryption of a sample dictionary."""
        security = Security(self.valid_key)
        sample_data = {"user": "test_user", "password": "test_password123"}
        try:
            encrypted_string = security.encrypt_data(sample_data)
            self.assertIsInstance(encrypted_string, str)
            # Further validation: try to decrypt to see if it's a valid token (done in roundtrip)
        except Exception as e:
            self.fail(f"Encryption failed for valid data: {e}")

    def test_encrypt_data_type_error_input_not_dict(self):
        """Test TypeError if the input data is not a dictionary."""
        security = Security(self.valid_key)
        with self.assertRaisesRegex(TypeError, "Data to encrypt must be a dictionary."):
            security.encrypt_data("this is not a dict")
        with self.assertRaisesRegex(TypeError, "Data to encrypt must be a dictionary."):
            security.encrypt_data([1, 2, 3])

    def test_encrypt_data_json_encode_error(self):
        """Test if JSONEncodeError is raised for non-serializable data."""
        security = Security(self.valid_key)
        # Sets are not directly JSON serializable by default json.dumps
        non_serializable_data = {"data": {1, 2, 3}}
        # Attempting to catch TypeError as json.JSONEncodeError seems unavailable directly
        # in this testing environment as json.JSONEncodeError, though security.py catches it.
        # json.dumps() itself raises TypeError for non-serializable objects if no default handler.
        with self.assertRaises(TypeError):
            security.encrypt_data(non_serializable_data)

    def test_decrypt_data_successful(self):
        """Test successful decryption of a valid encrypted string."""
        security = Security(self.valid_key)
        sample_data = {"message": "hello world"}
        encrypted_string = security.encrypt_data(sample_data) # Encrypt first

        try:
            decrypted_data = security.decrypt_data(encrypted_string)
            self.assertEqual(decrypted_data, sample_data)
        except Exception as e:
            self.fail(f"Decryption failed for valid encrypted string: {e}")

    def test_decrypt_data_type_error_input_not_string(self):
        """Test TypeError if the input encrypted_string is not a string."""
        security = Security(self.valid_key)
        with self.assertRaisesRegex(TypeError, "Encrypted data to decrypt must be a string."):
            security.decrypt_data(b"this is bytes, not str")
        with self.assertRaisesRegex(TypeError, "Encrypted data to decrypt must be a string."):
            security.decrypt_data({"data": "not a string"})

    def test_decrypt_data_invalid_token_malformed(self):
        """Test InvalidToken if the token is malformed."""
        security = Security(self.valid_key)
        malformed_token = "this_is_not_a_valid_fernet_token"
        with self.assertRaises(InvalidToken):
            security.decrypt_data(malformed_token)

    def test_decrypt_data_invalid_token_wrong_key(self):
        """Test InvalidToken if the token was encrypted with a different key."""
        security_encrypt = Security(self.valid_key)
        security_decrypt = Security(self.different_valid_key) # Use a different key for decryption
        sample_data = {"key": "value"}
        encrypted_string = security_encrypt.encrypt_data(sample_data)

        with self.assertRaises(InvalidToken):
            security_decrypt.decrypt_data(encrypted_string)

    def test_decrypt_data_json_decode_error(self):
        """Test JSONDecodeError if the decrypted data is not valid JSON."""
        security = Security(self.valid_key)
        # Manually create a valid Fernet token containing non-JSON data
        cipher = Fernet(self.valid_key)
        non_json_bytes = b"this is not json but is validly encrypted"
        encrypted_string_with_non_json = cipher.encrypt(non_json_bytes).decode('utf-8')

        with self.assertRaises(json.JSONDecodeError):
            security.decrypt_data(encrypted_string_with_non_json)

    def test_encrypt_decrypt_roundtrip(self):
        """Test that data remains consistent after encryption and decryption."""
        security = Security(self.valid_key)
        original_data = {
            "name": "Test User",
            "email": "test@example.com",
            "details": {"age": 30, "city": "Testville"},
            "numbers": [1, 2, 3, 4, 5]
        }

        encrypted_string = security.encrypt_data(original_data)
        self.assertIsInstance(encrypted_string, str)

        decrypted_data = security.decrypt_data(encrypted_string)
        self.assertEqual(original_data, decrypted_data)

    def test_encrypt_decrypt_roundtrip_empty_dict(self):
        """Test encrypt-decrypt roundtrip with an empty dictionary."""
        security = Security(self.valid_key)
        original_data = {}
        encrypted_string = security.encrypt_data(original_data)
        decrypted_data = security.decrypt_data(encrypted_string)
        self.assertEqual(original_data, decrypted_data)

if __name__ == '__main__':
    unittest.main()

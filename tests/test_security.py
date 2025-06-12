import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from linkedin_auto_applier.security import Security

class TestSecurity(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        sec = Security()
        data = {'foo': 'bar', 'num': 1}
        encrypted = sec.encrypt_data(data)
        self.assertIn('encrypted_data', encrypted)
        decrypted = sec.decrypt_data(encrypted)
        self.assertEqual(decrypted, data)

    def test_decrypt_invalid_data(self):
        sec = Security()
        result = sec.decrypt_data({'encrypted_data': 'invalid'})
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()

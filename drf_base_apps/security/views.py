"""Security views for encryption and decryption."""

import json

from cryptography.fernet import Fernet

from drf_base_config.settings import FERNET_KEY


class Security:
    """Security class for encryption and decryption operations."""

    f = Fernet(FERNET_KEY)

    def encrypt(self, value):
        """Encrypt a value using Fernet encryption."""
        return self.f.encrypt(self.__json_dumps(value).encode()).decode()

    def decrypt(self, value):
        """Decrypt a value using Fernet decryption."""
        return self.__json_loads(self.f.decrypt(value.encode()).decode())

    @staticmethod
    def __json_dumps(value):
        """Convert value to JSON string."""
        return json.dumps(value)

    @staticmethod
    def __json_loads(value):
        """Parse JSON string to value."""
        return json.loads(value)

"""
Encryption Utilities: AES-256-CBC and RSA-OAEP
Provides secure message encryption and key encryption
"""

import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional


class EncryptionManager:
    """Manages AES-256 message encryption and RSA-OAEP key encryption"""

    # AES Configuration
    AES_KEY_SIZE = 32  # 256 bits
    AES_BLOCK_SIZE = 16  # 128 bits (IV + block size)

    # RSA Configuration
    RSA_KEY_SIZE = 2048
    RSA_PUBLIC_EXPONENT = 65537

    @staticmethod
    def generate_aes_key() -> bytes:
        """Generate a random 256-bit AES key"""
        return os.urandom(EncryptionManager.AES_KEY_SIZE)

    @staticmethod
    def generate_rsa_keypair() -> Tuple[bytes, bytes]:
        """
        Generate RSA-2048 keypair

        Returns:
            (private_key_pem, public_key_pem): PEM-encoded keys as bytes
        """
        private_key = rsa.generate_private_key(
            public_exponent=EncryptionManager.RSA_PUBLIC_EXPONENT,
            key_size=EncryptionManager.RSA_KEY_SIZE,
            backend=default_backend(),
        )

        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    @staticmethod
    def load_private_key(pem: bytes):
        """Load private key from PEM bytes"""
        return serialization.load_pem_private_key(
            pem, password=None, backend=default_backend()
        )

    @staticmethod
    def load_public_key(pem: bytes):
        """Load public key from PEM bytes"""
        return serialization.load_pem_public_key(pem, backend=default_backend())

    @staticmethod
    def encrypt_message(plaintext: str, aes_key: bytes) -> str:
        """
        Encrypt message with AES-256-CBC

        Args:
            plaintext: Message to encrypt
            aes_key: 32-byte AES key

        Returns:
            Base64-encoded ciphertext with IV prepended
        """
        # Generate random IV
        iv = os.urandom(EncryptionManager.AES_BLOCK_SIZE)

        # Convert plaintext to bytes
        plaintext_bytes = plaintext.encode("utf-8")

        # PKCS7 Padding
        padding_length = EncryptionManager.AES_BLOCK_SIZE - (
            len(plaintext_bytes) % EncryptionManager.AES_BLOCK_SIZE
        )
        if padding_length == 0:
            padding_length = EncryptionManager.AES_BLOCK_SIZE

        padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)

        # Encrypt
        cipher = Cipher(
            algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Return IV + ciphertext as base64
        return base64.b64encode(iv + ciphertext).decode("utf-8")

    @staticmethod
    def decrypt_message(ciphertext_b64: str, aes_key: bytes) -> str:
        """
        Decrypt message encrypted with AES-256-CBC

        Args:
            ciphertext_b64: Base64-encoded ciphertext (with IV prepended)
            aes_key: 32-byte AES key

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        try:
            # Decode from base64
            ciphertext_with_iv = base64.b64decode(ciphertext_b64)

            # Extract IV and ciphertext
            iv = ciphertext_with_iv[: EncryptionManager.AES_BLOCK_SIZE]
            ciphertext = ciphertext_with_iv[EncryptionManager.AES_BLOCK_SIZE :]

            # Decrypt
            cipher = Cipher(
                algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove PKCS7 padding
            padding_length = padded_plaintext[-1]
            if not (1 <= padding_length <= EncryptionManager.AES_BLOCK_SIZE):
                raise ValueError("Invalid padding")

            # Verify padding
            if not all(b == padding_length for b in padded_plaintext[-padding_length:]):
                raise ValueError("Invalid padding")

            plaintext = padded_plaintext[:-padding_length]
            return plaintext.decode("utf-8")

        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")

    @staticmethod
    def encrypt_aes_key(aes_key: bytes, public_key) -> str:
        """
        Encrypt AES key with RSA public key using OAEP padding

        Args:
            aes_key: 32-byte AES key to encrypt
            public_key: RSA public key object

        Returns:
            Base64-encoded encrypted key
        """
        encrypted = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return base64.b64encode(encrypted).decode("utf-8")

    @staticmethod
    def decrypt_aes_key(encrypted_key_b64: str, private_key) -> bytes:
        """
        Decrypt AES key with RSA private key

        Args:
            encrypted_key_b64: Base64-encoded encrypted key
            private_key: RSA private key object

        Returns:
            Decrypted 32-byte AES key

        Raises:
            ValueError: If decryption fails
        """
        try:
            encrypted = base64.b64decode(encrypted_key_b64)
            aes_key = private_key.decrypt(
                encrypted,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            return aes_key
        except Exception as e:
            raise ValueError(f"Key decryption failed: {e}")

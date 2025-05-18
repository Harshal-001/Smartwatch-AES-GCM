import os
import time

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode
import traceback


def encrypt(plaintext, key=None, associated_data=None):
    """
    Encrypts plaintext using AES-GCM mode.

    Args:
        plaintext (bytes): The plaintext to encrypt
        key (bytes, optional): The encryption key (32 bytes for AES-256)
        associated_data (bytes, optional): Additional authenticated data

    Returns:
        tuple: (iv, ciphertext, tag)
    """
    # Generate random key if not provided
    if key is None:
        key = os.urandom(32)  # 256-bit key

    # Generate initialization vector
    iv = os.urandom(12)  # GCM recommended IV size

    # Create the cipher
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # Add associated data if provided
    if associated_data:
        encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    # Get authentication tag
    tag = encryptor.tag

    return key, iv, ciphertext, tag


def decrypt(iv, ciphertext, tag, key, associated_data=None):
    """
    Decrypts ciphertext using AES-GCM mode.

    Args:
        iv (bytes): Initialization vector
        ciphertext (bytes): The ciphertext to decrypt
        tag (bytes): Authentication tag
        key (bytes): The encryption key
        associated_data (bytes, optional): Additional authenticated data

    Returns:
        bytes: The decrypted plaintext
    """
    # Create the cipher
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # Add associated data if provided
    if associated_data:
        decryptor.authenticate_additional_data(associated_data)

    # Decrypt the ciphertext
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    return plaintext


def main():
    # Example usage
    plaintext = b"This is a secret message for AES-GCM testing."
    associated_data = b"Additional authenticated data"
    start_time = time.time()

    print("Original plaintext:", plaintext.decode())

    # Encrypt
    key, iv, ciphertext, tag = encrypt(plaintext, associated_data=associated_data)

    print("\nEncryption:")
    print(f"Key (base64): {b64encode(key).decode()}")
    print(f"IV (base64): {b64encode(iv).decode()}")
    print(f"Ciphertext (base64): {b64encode(ciphertext).decode()}")
    print(f"Auth Tag (base64): {b64encode(tag).decode()}")

    # Decrypt
    try:
        decrypted = decrypt(iv, ciphertext, tag, key, associated_data)
        print("\nDecryption successful!")
        print("Decrypted text:", decrypted.decode())
    except Exception as e:
        print("\nDecryption failed:", repr(e))
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")

    # Tamper with the ciphertext to demonstrate authentication
    print("\nTesting authentication by tampering with the ciphertext:")
    tampered_ciphertext = bytearray(ciphertext)
    if tampered_ciphertext:  # Make sure it's not empty
        tampered_ciphertext[0] ^= 1  # Flip a bit

    try:
        decrypted = decrypt(iv, bytes(tampered_ciphertext), tag, key, associated_data)
        print("Decryption successful (this shouldn't happen with tampered data)!")
        print("Decrypted text:", decrypted.decode())
    except Exception as e:
        print("Decryption failed as expected with error:")
        print(repr(e))
        print("\nThis is the expected behavior when the ciphertext has been tampered with!")
        print("AES-GCM provides authenticated encryption, so any tampering is detected.")


if __name__ == "__main__":
    main() 
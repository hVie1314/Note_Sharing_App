from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def generate_key(password: str) -> bytes:
    return password.encode('utf-8').ljust(32, b'\0')[:32]

def encrypt_note(note_content: str, password: str) -> dict:
    key = generate_key(password)
    iv = os.urandom(16)
    
    note_bytes = note_content.encode('utf-8')
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(note_bytes) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return {
        "content": ciphertext,
        "iv": iv
    }

def decrypt_note(encrypted_note: dict, password: str) -> str:
    key = generate_key(password)
    iv = encrypted_note["iv"]
    ciphertext = encrypted_note["content"]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    original_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return original_data.decode('utf-8')

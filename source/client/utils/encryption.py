from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os


def encrypt_file(file_path: str, key: bytes) -> dict:
    iv = os.urandom(16)
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as f:
        f.write(iv + ciphertext)

    return {
        "file_path": encrypted_file_path
    }

def decrypt_file(encrypted_file_path: str, key: bytes) -> str:
    with open(encrypted_file_path, 'rb') as f:
        iv = f.read(16)
        ciphertext = f.read()
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    original_data = unpadder.update(decrypted_data) + unpadder.finalize()

    decrypted_file_path = encrypted_file_path.replace('.enc', '.dec')
    with open(decrypted_file_path, 'wb') as f:
        f.write(original_data)

    return decrypted_file_path
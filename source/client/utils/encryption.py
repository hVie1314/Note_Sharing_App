from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def generate_key(password: str) -> bytes:
    """
    Chuyển đổi password thành key 32 bytes cho AES-256
    """
    # Padding password để đủ 32 bytes
    return password.encode('utf-8').ljust(32, b'\0')[:32]

def encrypt_note(content, password):
    try:
        # Generate key 32 bytes từ password
        key = generate_key(password)
        
        # Generate IV
        iv = os.urandom(16)
        
        # Tạo cipher
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),  
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Padding content
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(content) + padder.finalize()
        
        # Mã hóa
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'ciphertext': ciphertext,
            'iv': iv,
            'key': key  # Thêm key vào response
        }
        
    except Exception as e:
        print(f"Encryption error: {str(e)}")
        raise

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

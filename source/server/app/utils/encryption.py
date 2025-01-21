from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

# Hàm tạo khóa AES
def generate_key(password: str) -> bytes:
    # Dùng hash SHA-256 của mật khẩu làm khóa AES
    return password.encode('utf-8').ljust(32, b'\0')[:32]  # 32 bytes cho AES-256

# Hàm mã hóa ghi chú
def encrypt_note(note_content: str, password: str) -> dict:
    key = generate_key(password)  # Tạo khóa từ mật khẩu
    iv = os.urandom(16)  # Tạo vector khởi tạo ngẫu nhiên 16 bytes cho CBC mode
    
    # Chuyển đổi nội dung ghi chú thành bytes
    note_bytes = note_content.encode('utf-8')

    # Padding dữ liệu để nó có độ dài bội số của block size (16 bytes cho AES)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(note_bytes) + padder.finalize()

    # Khởi tạo AES cipher với chế độ CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Mã hóa dữ liệu
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Trả về kết quả dưới dạng dictionary (bao gồm ciphertext và iv)
    return {
        "ciphertext": ciphertext,
        "iv": iv
    }

# Hàm giải mã ghi chú
def decrypt_note(encrypted_note: dict, password: str) -> str:
    key = generate_key(password)
    iv = encrypted_note["iv"]
    ciphertext = encrypted_note["ciphertext"]

    # Khởi tạo AES cipher với chế độ CBC
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Giải mã dữ liệu
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()

    # Loại bỏ padding
    unpadder = padding.PKCS7(128).unpadder()
    original_data = unpadder.update(decrypted_data) + unpadder.finalize()

    # Chuyển lại thành chuỗi
    return original_data.decode('utf-8')
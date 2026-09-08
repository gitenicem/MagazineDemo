from cryptography.fernet import Fernet
import re

key = Fernet(b'c7rcLXvox85-_nX66iNRWmvZkb4bSo-K3rE1KmansKc=')

def encrypt_password(password: str):
    return key.encrypt(password.encode()).decode("utf-8")

def decrypt_password(password: str):
    return key.decrypt(password.encode()).decode("utf-8")

def is_encrypt_password(password: str) -> bool:
    return bool(re.match(r'^gAAAAA[A-Za-z0-9_\-]+=*$', password))
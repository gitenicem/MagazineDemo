import bcrypt
import re

def is_hashed(value: str) -> bool:
    return bool(re.match(r"^\$2[aby]\$\d{2}\$.{53}$", value))

def hash_password(password: str) -> str :
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(12))
    return password_hash.decode("utf-8")

def check_password(password: str, hashed_password) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
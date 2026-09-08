from helpers.crypto import encrypt_password, decrypt_password, is_encrypt_password
import configparser
import os

def config_path():
    if os.name == "nt":  # Windows > C:\Users\usuario\AppData\Roaming
        base = os.getenv("APPDATA")
    else:  # Linux / Mac > home/usuario/.config
        base = os.path.join(os.path.expanduser("~"), ".config")

    path = os.path.join(base, "MagConfig") # type: ignore
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, "config.ini")

def cargar_config():
    cfg = configparser.ConfigParser()
    ruta = config_path()

    if not os.path.exists(ruta):
        cfg["app"] = {
            "theme": "light"
        }
        cfg["operation"] = {
            "modo": "FLUJO",
            "alias": "SMT1",
        }
        cfg["database"] = {
            "host": "LAPTOP-MFL99FU0.local",
            "port": "3306",
            "user": "devuser",
            "password": encrypt_password("devpass123"),
            "name": "jabil"
        }
        guardar_config(cfg)
    else:
        cfg.read(ruta)
        if not is_encrypt_password(cfg.get("database", "password")):
            cfg.set("database", "password", encrypt_password(cfg.get("database", "password")))
            guardar_config(cfg)

    return cfg

def guardar_config(config):
    with open(config_path(), "w") as f:
        config.write(f)

def save_theme(value: str):
    config.set("app", "theme", value)
    guardar_config(config)

config = cargar_config()
theme = config.get("app", "theme", fallback="light")

db_config = {
    "host": config.get("database", "host"),
    "port": config.getint("database", "port"),
    "user": config.get("database", "user"),
    "password": decrypt_password(config.get("database", "password")),
    "database": config.get("database", "name"),
    "raise_on_warnings": True,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "use_pure": True
}
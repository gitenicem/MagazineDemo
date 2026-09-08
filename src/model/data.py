import json
from dataclasses import asdict
from threading import Lock
from datetime import datetime

from helpers.bcript import is_hashed, check_password, hash_password
from helpers.crypto import encrypt_password, decrypt_password, is_encrypt_password

#import bcrypt

from model.conexion import DAO
from helpers.config import db_config


class DataAccess:
    __conexion = None
    __candado = None
    __estaciones_version = 0
    __amr_config_version = 0
    __estaciones_detectadas_version = 0
    __manager_config_version = 0
    __estaciones_config_version = 0

    def __init__(self):
        DataAccess.__candado = Lock()
        if DataAccess.__conexion is None:
            DataAccess.__conexion = DAO(db_config)




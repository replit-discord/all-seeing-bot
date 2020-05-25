import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def prep(key, string):
    password = key.encode()

    salt = os.environ.get('SALT').encode()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    KEY = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(KEY)
    string = bytes(string, 'utf-8')
    return f, string


def encode(key, string):

    key, string = prep(key, string)

    return key.encrypt(string).decode()


def decode(key, string):
    key, string = prep(key, string)

    return key.decrypt(string).decode()

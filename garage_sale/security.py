import base64
import os

from cryptography.fernet import Fernet
from passlib.hash import argon2

from garage_sale import server_dir

pep_file = os.path.join(server_dir, "../pepper.bin")

key = Fernet.generate_key()
pep = Fernet(key)  #
# WRITE Pepper
with open("../pepper.bin", 'wb') as file:
    file.write(key)

with open(pep_file, 'rb') as fin:
    key = fin.read()  #
    pep = Fernet(key)


def hash_password(pwd, pep):
    h = argon2.using(rounds=10).hash(pwd)
    ph = pep.encrypt(h.encode('utf-8'))
    b64ph = base64.b64encode(ph)
    return b64ph


def check_password(pwd, b64ph, pep):
    ph = base64.b64decode(b64ph)
    h = pep.decrypt(ph)
    return argon2.verify(pwd, h)

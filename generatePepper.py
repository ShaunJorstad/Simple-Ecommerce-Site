import base64 
from cryptography.fernet import Fernet 
from passlib.hash import bcrypt_sha256 
from passlib.hash import argon2
import os

key = Fernet.generate_key()
pep = Fernet(key)#
# WRITE Pepper
with open("pepper.bin", 'wb') as fout:
    fout.write(key)

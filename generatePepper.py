from cryptography.fernet import Fernet

key = Fernet.generate_key()
pep = Fernet(key)  #
# WRITE Pepper
with open("pepper.bin", 'wb') as file:
    file.write(key)

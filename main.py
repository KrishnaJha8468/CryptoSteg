import hashlib
from Crypto.Cipher import AES

class AES256:
    def __init__(self):
        self.key = None
    
    def set_password(self, password):
        self.key = hashlib.sha256(password.encode()).digest()
        print(f"Password set: {'*' * len(password)}")

print("CryptoSteg v0.2 - Encryption module added")

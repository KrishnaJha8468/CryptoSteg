import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


class AESEncryptor:
    
    
    def __init__(self):
        self.key = None
        self.password = None
    
    def set_password(self, password: str):
        
        self.password = password
        
        self.key = hashlib.sha256(password.encode()).digest()
    
    def encrypt(self, plaintext: str) -> bytes:
        
        if not self.key:
            raise ValueError("Set password first!")
        
        
        iv = get_random_bytes(16)
        
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        
        padded = pad(plaintext.encode(), AES.block_size)
        ciphertext = cipher.encrypt(padded)
        
        
        return iv + ciphertext
    
    def decrypt(self, encrypted: bytes) -> str:
        
        if not self.key:
            raise ValueError("Set password first!")
        
        
        iv = encrypted[:16]
        ciphertext = encrypted[16:]
        
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        
        
        plaintext = unpad(decrypted, AES.block_size)
        return plaintext.decode()



if __name__ == "__main__":
    crypto = AESEncryptor()
    crypto.set_password("secret123")
    
    msg = "Hello Softwarica!"
    encrypted = crypto.encrypt(msg)
    decrypted = crypto.decrypt(encrypted)
    
    print(f"Original: {msg}")
    print(f"Encrypted (hex): {encrypted.hex()}")
    print(f"Decrypted: {decrypted}")
    print("✅ Encryption works!")
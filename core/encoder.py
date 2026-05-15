from .encryption import AESEncryptor
from .steganography import LSBSteganography


class Encoder:
    
    def __init__(self):
        self.crypto = AESEncryptor()
        self.stego = LSBSteganography()
    
    def encode(self, image_path: str, message: str, password: str, output_path: str) -> dict:
        self.crypto.set_password(password)
        encrypted_data = self.crypto.encrypt(message)
        
        
        bytes_hidden = self.stego.hide(image_path, encrypted_data, output_path)
        
        return {
            'success': True,
            'bytes_hidden': bytes_hidden,
            'original_message_length': len(message),
            'encrypted_size': len(encrypted_data),
            'output_path': output_path
        }



if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    
    
    test_img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8))
    test_img.save("test_img.png")
    
    encoder = Encoder()
    result = encoder.encode(
        image_path="test_img.png",
        message="Top Secret Message!",
        password="agent007",
        output_path="hidden.png"
    )
    
    print(f"Result: {result}")
    
    
    import os
    os.remove("test_img.png")
    os.remove("hidden.png")
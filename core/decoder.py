from .encryption import AESEncryptor
from .steganography import LSBSteganography


class Decoder:
    
    
    def __init__(self):
        self.crypto = AESEncryptor()
        self.stego = LSBSteganography()
    
    def decode(self, image_path: str, password: str) -> dict:
       
        
        extracted_data = self.stego.extract(image_path)
        
        if extracted_data is None:
            return {
                'success': False,
                'error': 'No hidden data found in this image!'
            }
        
        
        try:
            self.crypto.set_password(password)
            decrypted_message = self.crypto.decrypt(extracted_data)
            
            return {
                'success': True,
                'message': decrypted_message,
                'encrypted_size': len(extracted_data)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Wrong password or corrupted data!'
            }



if __name__ == "__main__":
    from .encoder import Encoder
    
    
    from PIL import Image
    import numpy as np
    
    test_img = Image.fromarray(np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8))
    test_img.save("test.png")
    
    encoder = Encoder()
    encoder.encode("test.png", "Secret Message", "pass123", "hidden.png")
    
    
    decoder = Decoder()
    result = decoder.decode("hidden.png", "pass123")
    print(f"Decode result: {result}")
    
    
    result2 = decoder.decode("hidden.png", "wrongpass")
    print(f"Wrong password result: {result2}")
    
    
    import os
    os.remove("test.png")
    os.remove("hidden.png")
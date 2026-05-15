from PIL import Image
import numpy as np


class LSBSteganography:

    END_MARKER = '1111111111111110'  # 16 bits of marker
    
    @staticmethod
    def text_to_binary(text: bytes) -> str:
        return ''.join(format(byte, '08b') for byte in text)
    
    @staticmethod
    def binary_to_text(binary: str) -> bytes:
        
        return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))
    
    def hide(self, image_path: str, secret_data: bytes, output_path: str) -> int:
        
        # Open image
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = np.array(img)
        
        # Convert data to binary with end marker
        binary_data = self.text_to_binary(secret_data) + self.END_MARKER
        
        height, width, channels = pixels.shape
        max_bits = height * width * 3
        
        if len(binary_data) > max_bits:
            raise ValueError(f"Data too large! Need {len(binary_data)} bits, but only {max_bits} bits available")
        
        # Hide bits in LSB of each pixel channel
        bit_index = 0
        for i in range(height):
            for j in range(width):
                for k in range(3):  # RGB channels
                    if bit_index < len(binary_data):
                        # Clear LSB and set to our bit
                        pixels[i][j][k] = (pixels[i][j][k] & 0xFE) | int(binary_data[bit_index])
                        bit_index += 1
                    else:
                        break
                if bit_index >= len(binary_data):
                    break
            if bit_index >= len(binary_data):
                break
        
        # Save new image
        hidden_img = Image.fromarray(pixels)
        hidden_img.save(output_path, 'PNG')
        
        return len(secret_data)
    
    def extract(self, image_path: str) -> bytes:
        
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = np.array(img)
        
        binary_data = ""
        
        height, width, channels = pixels.shape
        
        for i in range(height):
            for j in range(width):
                for k in range(3):
                    # Get LSB
                    binary_data += str(pixels[i][j][k] & 1)
                    
                    #  for end marker every 16 bits
                    if len(binary_data) >= 16 and binary_data[-16:] == self.END_MARKER:
                        
                        binary_data = binary_data[:-16]
                        return self.binary_to_text(binary_data)
        
        
        return None



if __name__ == "__main__":
    stego = LSBSteganography()
    
    
    from PIL import Image
    import numpy as np
    
    test_img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    test_img.save("test_input.png")
    
    
    secret = b"Hello World!"
    stego.hide("test_input.png", secret, "test_output.png")
    print(f"Hidden: {secret}")
    
    
    extracted = stego.extract("test_output.png")
    print(f"Extracted: {extracted}")
    
    if secret == extracted:
        print("✅ LSB Steganography works!")
    
    
    import os
    os.remove("test_input.png")
    os.remove("test_output.png")
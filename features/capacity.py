from PIL import Image


class CapacityChecker:
    
    @staticmethod
    def calculate(image_path: str) -> dict:
       
        img = Image.open(image_path)
        width, height = img.size
        
        total_pixels = width * height
        total_bits = total_pixels * 3  # RGB channels
        total_bytes = total_bits // 8
        
        # Reserve 16 bytes for IV + some overhead
        usable_bytes = total_bytes - 32
        
       
        max_chars = usable_bytes
        
        return {
            'width': width,
            'height': height,
            'total_pixels': total_pixels,
            'total_bits': total_bits,
            'total_bytes': total_bytes,
            'usable_bytes': max(0, usable_bytes),
            'max_characters': max(0, max_chars),
            'is_sufficient': True
        }
    
    @staticmethod
    def can_hide(image_path: str, message: str) -> dict:
        
        capacity = CapacityChecker.calculate(image_path)
        message_bytes = len(message.encode('utf-8'))
        
        
        total_needed = message_bytes + 32
        
        return {
            'can_hide': total_needed <= capacity['usable_bytes'],
            'message_size': message_bytes,
            'capacity': capacity['usable_bytes'],
            'remaining': capacity['usable_bytes'] - total_needed
        }



if __name__ == "__main__":
    from PIL import Image
    import numpy as np
    
    
    img = Image.fromarray(np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8))
    img.save("test.png")
    
    capacity = CapacityChecker.calculate("test.png")
    print(f"Capacity: {capacity}")
    
    
    import os
    os.remove("test.png")
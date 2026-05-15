from PIL import Image
import numpy as np

# Create a test image (larger this time)
img = Image.new('RGB', (200, 200), color='white')
pixels = np.array(img)
print(f"Test image size: {pixels.shape}")

# Test LSB extraction
lsb_vals = [p & 1 for p in pixels[:,:,0].flatten()[:10000]]
ones = sum(lsb_vals)
print(f"LSB test: Ones={ones}, Total={len(lsb_vals)}")
print("✅ Test passed - no out of bounds error!")
from PIL import Image
import sys

img_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
img = Image.open(img_path).convert('RGB')
w, h = img.size
print(f"Size: {w}x{h}")

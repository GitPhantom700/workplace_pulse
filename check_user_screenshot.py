from PIL import Image
img = Image.open('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png').convert('RGB')
print(f"User screenshot size: {img.size}")

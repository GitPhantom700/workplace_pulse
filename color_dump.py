from PIL import Image
img = Image.open('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png').convert('RGB')
pixels = img.load()
for x in range(700, 1000, 20):
    print(f"x={x}: {pixels[x, 20]}")

from PIL import Image

img = Image.open('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png').convert('RGB')
w, h = img.size
for y in range(h):
    for x in range(w):
        r, g, b = img.getpixel((x, y))
        if r < 140 and g < 140 and b < 140 and r > 30:
            print(f"Text pixel at {x}, {y}: {r},{g},{b}")

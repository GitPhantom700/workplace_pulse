from PIL import Image

pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
img_pre = Image.open(pre_path).convert('RGB')
w2, h2 = img_pre.size
pixels_pre = img_pre.load()

g_x, g_y = [], []
for y in range(5, 50):
    for x in range(950, w2):
        r, g, b = pixels_pre[x, y]
        # Look for pure blue or red from google logo
        if b > 200 and r < 100 and g < 150: # Blue
            g_x.append(x)
            g_y.append(y)
if g_x:
    print(f"Pre-Login 'Google Logo' found around: x={min(g_x)}-{max(g_x)}, y={min(g_y)}-{max(g_y)}")

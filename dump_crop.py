from PIL import Image
img = Image.open('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png').convert('RGB')
w, h = img.size
# find red pixels
red_x = []
for y in range(h):
    for x in range(w):
        r, g, b = img.getpixel((x, y))
        if r > 200 and g < 50 and b < 50:
            red_x.append(x)
print(f"Red pixels x: min={min(red_x)}, max={max(red_x)}")

# find green pixels (ON)
green_x = []
for y in range(h):
    for x in range(w):
        r, g, b = img.getpixel((x, y))
        if r < 100 and g > 100 and b < 100:
            green_x.append(x)
if green_x:
    print(f"Green pixels x: min={min(green_x)}, max={max(green_x)}")

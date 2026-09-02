from PIL import Image

def draw_ascii(path, w_max=120):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    ratio = w / w_max
    new_h = int(h / ratio)
    img = img.resize((w_max, new_h))
    
    for y in range(new_h):
        line = ""
        for x in range(w_max):
            r, g, b = img.getpixel((x, y))
            if r > 150 and g < 100 and b < 100:
                line += "R" # Red
            elif r < 100 and g > 150 and b < 100:
                line += "G"
            elif r < 100 and g < 100 and b > 150:
                line += "B"
            elif r < 100 and g < 100 and b < 100:
                line += "T" # Text/Dark
            else:
                line += " "
        print(line)

print("Crop image pre-login:")
draw_ascii('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png', 100)
print("Crop image post-login:")
draw_ascii('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322715471.png', 100)


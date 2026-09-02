from PIL import Image

def draw_ascii(path, w_max=80):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    ratio = w / w_max
    new_h = int(h / ratio)
    img = img.resize((w_max, new_h))
    
    for y in range(new_h):
        line = ""
        for x in range(w_max):
            r, g, b = img.getpixel((x, y))
            if r > 200 and g < 50 and b < 50:
                line += "R" # Red
            elif r < 100 and g > 100 and b < 100:
                line += "G" # Green
            elif r < 100 and g < 100 and b > 150:
                line += "B" # Blue
            elif r < 120 and g < 120 and b < 120:
                line += "T" # Text/Dark
            elif r > 240 and g > 240 and b > 240:
                line += "W" # White
            else:
                line += "." # Gray/Other
        print(line)

print("Crop image:")
draw_ascii('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png', 70)

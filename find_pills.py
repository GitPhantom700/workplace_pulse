from PIL import Image

def find_pills(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    pixels = img.load()
    
    # scan y=16, look for white pixels
    white_segments = []
    in_white = False
    start_x = 0
    for x in range(600, w):
        r, g, b = pixels[x, 16]
        # white or very light grey border
        if r > 240 and g > 240 and b > 240:
            if not in_white:
                in_white = True
                start_x = x
        else:
            if in_white:
                in_white = False
                if x - start_x > 30: # at least 30px wide
                    white_segments.append((start_x, x))
    print(f"White segments at y=16: {white_segments}")

print("Post-Login:")
find_pills('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png')
print("Pre-Login:")
find_pills('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png')

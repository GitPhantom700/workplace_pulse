from PIL import Image

def find_elements():
    # Post-login
    post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
    img = Image.open(post_path).convert('RGB')
    w, h = img.size
    pixels = img.load()
    
    # 1. Find "OFF" (Orange text)
    off_x, off_y = [], []
    for y in range(5, 50):
        for x in range(600, w):
            r, g, b = pixels[x, y]
            if r > 200 and g > 100 and g < 180 and b < 50: # Orange
                off_x.append(x)
                off_y.append(y)
    
    if off_x:
        print(f"Post-Login 'OFF' found around: x={min(off_x)}-{max(off_x)}, y={min(off_y)}-{max(off_y)}")
    
    # Pre-login
    pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
    img_pre = Image.open(pre_path).convert('RGB')
    w2, h2 = img_pre.size
    pixels_pre = img_pre.load()
    
    # Find "ON" (Green text)
    on_x, on_y = [], []
    for y in range(5, 50):
        for x in range(600, w2):
            r, g, b = pixels_pre[x, y]
            if r < 100 and g > 120 and b < 100: # Green
                on_x.append(x)
                on_y.append(y)
                
    if on_x:
        print(f"Pre-Login 'ON' found around: x={min(on_x)}-{max(on_x)}, y={min(on_y)}-{max(on_y)}")

find_elements()

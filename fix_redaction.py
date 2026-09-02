from PIL import Image, ImageDraw

paths = [
    '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-auth-save-redacted.png',
    '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-auth-save-redacted.png',
    '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-auth-save.png',
    '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788319945573.png'
]

for p in paths:
    try:
        img = Image.open(p).convert('RGB')
        draw = ImageDraw.Draw(img)
        w, h = img.size
        # The dropdown is somewhere below the middle. 
        # "Support email for project" text is around y=320 or y=330?
        # Let's just cover everything from x=150 to x=600, y=340 to y=400.
        # Let's find the exact blue border to be smart.
        pixels = img.load()
        min_y, max_y = h, 0
        min_x, max_x = w, 0
        for y in range(int(h/2), h):
            for x in range(50, w-50):
                r, g, b = pixels[x, y]
                # Look for dark grey text of the email or blue border
                if b > 200 and r < 50 and g < 150: # blue border
                    if y < min_y: min_y = y
                    if y > max_y: max_y = y
                    if x < min_x: min_x = x
                    if x > max_x: max_x = x
        
        # Draw a white box strictly inside the blue border
        if max_y > min_y:
            draw.rectangle([min_x+2, min_y+2, max_x-20, max_y-2], fill=(255,255,255))
            print(f"Redacted box at {min_x}, {min_y}, {max_x}, {max_y} for {p}")
            img.save(p.replace('.png', '-redacted-v2.png'))
            # overwrite the original redacted one as well to be safe
            if 'redacted' in p:
                img.save(p)
    except Exception as e:
        print(f"Error processing {p}: {e}")

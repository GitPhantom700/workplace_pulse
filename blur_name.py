from PIL import Image, ImageFilter, ImageDraw
import sys

img_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-dashboard.png'
img = Image.open(img_path).convert('RGB')
pixels = img.load()
width, height = img.size

# Find bounds of the orange text "Hello, Chandraprakash"
min_x, min_y = width, height
max_x, max_y = 0, 0

for y in range(int(height * 0.1), int(height * 0.4)): # upper half where title is
    for x in range(int(width * 0.05), int(width * 0.5)): # left side
        r, g, b = pixels[x, y]
        # Detect the orange/red gradient
        if r > 200 and g < 180 and b < 50:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y

if max_x > min_x and max_y > min_y:
    print(f"Found orange text at: {min_x}, {min_y}, {max_x}, {max_y}")
    # Expand box slightly
    min_x = max(0, min_x - 10)
    max_x = min(width, max_x + 10)
    min_y = max(0, min_y - 10)
    max_y = min(height, max_y + 10)
    
    # We want to blur just "Chandraprakash", not "Hello,"
    # "Hello, " is roughly the first 30-40% of the width.
    # Let's just blur the whole thing, or maybe block it out with a gray box
    box = (min_x, min_y, max_x, max_y)
    
    # Actually, the user's uploaded image (the crop) just says "Chandraprakash"
    # Let's draw a neat grey rounded rectangle over the text to "redact" it cleanly, 
    # or apply a Gaussian blur to the cropped region.
    
    # Let's apply a heavy blur
    icrop = img.crop(box)
    for _ in range(5):
        icrop = icrop.filter(ImageFilter.GaussianBlur(radius=10))
    img.paste(icrop, box)
    
    img.save(img_path)
    # Also save to artifact dir
    img.save('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-dashboard.png')
    print("Image redacted successfully.")
else:
    print("Could not find the orange text.")

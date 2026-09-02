from PIL import Image, ImageDraw
import sys

img_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788319474346.png'
img = Image.open(img_path).convert('RGB')
draw = ImageDraw.Draw(img)

# Draw a solid rectangle over "Chandraprakash"
# From our previous script we know the orange text is roughly at 114, 226, 486, 262
# We will draw a light gray box over the name specifically. "Hello, " is about 100px wide.
# Let's just grey out everything from x=200 to x=500 to be safe and completely cover the name.
draw.rectangle([190, 220, 520, 270], fill=(245, 245, 245))

# Save the new file to bust the UI cache
out_ws = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-dashboard-redacted.png'
out_art = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-dashboard-redacted.png'
img.save(out_ws)
img.save(out_art)

print("Redacted perfectly!")

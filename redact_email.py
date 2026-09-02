from PIL import Image, ImageDraw

# The image to modify
img_path = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-auth-save.png'
img = Image.open(img_path).convert('RGB')
draw = ImageDraw.Draw(img)

# In the firebase-auth-save.png image (806x639), the email dropdown is located
# roughly in the middle, below "Support email for project".
# Let's draw a solid white/grey box over the text inside the dropdown box.
# Coordinates estimated based on the UI layout:
draw.rectangle([160, 545, 500, 580], fill=(255, 255, 255))

# Save the modified image with a new name to bust cache
out_ws = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-auth-save-redacted.png'
out_art = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-auth-save-redacted.png'
img.save(out_ws)
img.save(out_art)
print("Redacted perfectly!")

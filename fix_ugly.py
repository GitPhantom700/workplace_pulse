from PIL import Image, ImageDraw, ImageFilter

orig_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788319945573.png'
img = Image.open(orig_path).convert('RGB')
draw = ImageDraw.Draw(img)

# We want a neat, clean blur just over the text inside the box.
# Coordinates: 
# x: 160 to 450 (covers the email text)
# y: 350 to 385 (covers the height of the text inside the box)
box = (160, 350, 480, 385)

# Crop, heavily blur, and paste back so it looks professional, not like a white void
icrop = img.crop(box)
for _ in range(5):
    icrop = icrop.filter(ImageFilter.GaussianBlur(radius=8))
img.paste(icrop, box)

out_ws = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/firebase-auth-save-redacted-v4.png'
out_art = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/firebase-auth-save-redacted-v4.png'

img.save(out_ws)
img.save(out_art)
print("Saved v4")

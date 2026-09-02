from PIL import Image, ImageDraw, ImageFilter

# 1. Process Post-Login Screen (media_1788322360451.png)
post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
img = Image.open(post_path).convert('RGB')
draw = ImageDraw.Draw(img)

# Coords for top right corner in 1024x609 image
# Demo Mode OFF is around (780, 10, 860, 40)
# Profile Name/Photo is around (870, 10, 950, 40)
# Log Out is around (960, 10, 1010, 40)

# Redact the name/photo but keep it looking like a username component.
# Let's draw a generic grey circle for the photo, and a solid grey rounded rectangle for the name/email.
draw.ellipse([870, 15, 895, 40], fill=(200, 200, 200)) # Fake avatar
draw.rectangle([905, 18, 970, 26], fill=(220, 220, 220)) # Fake Name
draw.rectangle([905, 29, 985, 35], fill=(230, 230, 230)) # Fake Email

# Highlight Demo Mode OFF with a red box
draw.rectangle([780, 12, 855, 42], outline=(255, 0, 0), width=2)
# Highlight Log Out with a red box
draw.rectangle([990, 12, 1015, 42], outline=(255, 0, 0), width=2)
# Highlight the fake profile component with a red box
draw.rectangle([865, 12, 987, 42], outline=(255, 0, 0), width=2)

out_ws_post = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png'
out_art_post = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png'
img.save(out_ws_post)
img.save(out_art_post)

# 2. Process Pre-Login Screen (media_1788322473314.png)
pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
img_pre = Image.open(pre_path).convert('RGB')
draw_pre = ImageDraw.Draw(img_pre)

# Highlight Demo Mode ON
draw_pre.rectangle([860, 12, 930, 42], outline=(255, 0, 0), width=2)
# Highlight Sign In
draw_pre.rectangle([940, 12, 1015, 42], outline=(255, 0, 0), width=2)

out_ws_pre = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png'
out_art_pre = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png'
img_pre.save(out_ws_pre)
img_pre.save(out_art_pre)

print("Images processed.")

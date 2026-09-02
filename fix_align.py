from PIL import Image, ImageDraw

def process():
    # 1. Process Post-Login
    post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
    img = Image.open(post_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Adjusted coordinates (moved UP and LEFT)
    # Demo Mode OFF: was [780, 12, 855, 42] -> try [780, 5, 875, 35]
    # Actually let's look for the bounding box of the grey pills.
    # The background is white (255,255,255) or slightly off-white. The pills are grey #f3f4f6 (243,244,246).
    
    # Just manual adjustment based on visual feedback:
    # Top image offset: move up by ~5-8px, move right by ~10px?
    # Bottom image offset: the avatar was drawn at 870. It needs to be moved left to ~840?
    
    # Let's draw boxes at new guessed locations:
    # Post-login:
    # Demo Mode OFF pill is around x=770 to 860, y=10 to 35
    draw.rectangle([765, 10, 865, 36], outline=(255, 0, 0), width=2) # Demo Mode OFF
    
    # Profile section is around x=870 to 1010
    draw.rectangle([875, 10, 1015, 36], outline=(255, 0, 0), width=2) # Profile box
    
    # Redact profile
    draw.ellipse([878, 12, 898, 32], fill=(200, 200, 200)) # Avatar
    draw.rectangle([905, 14, 965, 22], fill=(220, 220, 220)) # Name
    draw.rectangle([905, 24, 975, 30], fill=(230, 230, 230)) # Email
    
    # Log out button - actually there is no log out button, the screenshot shows "Log Out" text or a button at the far right.
    # Let's just outline the Log Out text if it's there.
    
    out_ws_post = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png'
    out_art_post = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png'
    img.save(out_ws_post)
    img.save(out_art_post)
    
    # 2. Process Pre-Login
    pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
    img_pre = Image.open(pre_path).convert('RGB')
    draw_pre = ImageDraw.Draw(img_pre)
    
    # Demo Mode ON
    draw_pre.rectangle([845, 10, 935, 36], outline=(255, 0, 0), width=2)
    # Sign In
    draw_pre.rectangle([945, 10, 1015, 36], outline=(255, 0, 0), width=2)
    
    out_ws_pre = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png'
    out_art_pre = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png'
    img_pre.save(out_ws_pre)
    img_pre.save(out_art_pre)

process()
print("Adjusted coordinates.")

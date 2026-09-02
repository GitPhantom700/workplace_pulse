from PIL import Image, ImageDraw

def process():
    # 1. Post-Login
    post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
    img = Image.open(post_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Redact profile First
    # Avatar is left of text (840) -> ~815
    draw.ellipse([812, 10, 838, 36], fill=(200, 200, 200))
    # Name + Email
    draw.rectangle([845, 14, 955, 23], fill=(220, 220, 220))
    draw.rectangle([845, 25, 955, 31], fill=(230, 230, 230))
    
    # Draw boxes
    # Demo Mode OFF (Text 741-782)
    draw.rectangle([720, 8, 800, 38], outline=(255, 0, 0), width=3)
    
    # Profile + Log Out (Avatar 815, Log Out 999)
    # The user asked to highlight 3 components: Demo Mode, user's name, log out.
    # We can draw one big box or two separate boxes. I'll draw two separate boxes to match exactly the 3 components requested.
    draw.rectangle([805, 8, 960, 38], outline=(255, 0, 0), width=3) # Profile box
    draw.rectangle([965, 8, 1015, 38], outline=(255, 0, 0), width=3) # Log out box
    
    out_ws_post = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png'
    out_art_post = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png'
    img.save(out_ws_post)
    img.save(out_art_post)
    
    # 2. Pre-Login
    pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
    img_pre = Image.open(pre_path).convert('RGB')
    draw_pre = ImageDraw.Draw(img_pre)
    
    # Demo Mode ON (Text 868-907)
    draw_pre.rectangle([845, 8, 930, 38], outline=(255, 0, 0), width=3)
    # Sign In (Text 958-994)
    draw_pre.rectangle([940, 8, 1010, 38], outline=(255, 0, 0), width=3)
    
    out_ws_pre = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png'
    out_art_pre = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png'
    img_pre.save(out_ws_pre)
    img_pre.save(out_art_pre)

process()
print("Images fully aligned!")

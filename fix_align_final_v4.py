from PIL import Image, ImageDraw

def process():
    # We will shift all y coordinates UP by 12 pixels.
    Y_SHIFT = 12
    
    # 1. Post-Login
    post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
    img = Image.open(post_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Redact profile
    # Old Avatar: [812, 10, 838, 36]
    draw.ellipse([812, max(0, 10-Y_SHIFT), 838, 36-Y_SHIFT], fill=(200, 200, 200))
    # Old Name + Email: [845, 14, 955, 23], [845, 25, 955, 31]
    draw.rectangle([845, max(0, 14-Y_SHIFT), 955, 23-Y_SHIFT], fill=(220, 220, 220))
    draw.rectangle([845, max(0, 25-Y_SHIFT), 955, 31-Y_SHIFT], fill=(230, 230, 230))
    
    # Draw boxes
    # Demo Mode OFF
    draw.rectangle([720, max(0, 8-Y_SHIFT), 800, 38-Y_SHIFT], outline=(255, 0, 0), width=3)
    # Profile + Log Out
    draw.rectangle([805, max(0, 8-Y_SHIFT), 960, 38-Y_SHIFT], outline=(255, 0, 0), width=3)
    draw.rectangle([965, max(0, 8-Y_SHIFT), 1015, 38-Y_SHIFT], outline=(255, 0, 0), width=3)
    
    out_ws_post = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png'
    out_art_post = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-post.png'
    img.save(out_ws_post)
    img.save(out_art_post)
    
    # 2. Pre-Login
    pre_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png'
    img_pre = Image.open(pre_path).convert('RGB')
    draw_pre = ImageDraw.Draw(img_pre)
    
    # Demo Mode ON
    draw_pre.rectangle([845, max(0, 8-Y_SHIFT), 930, 38-Y_SHIFT], outline=(255, 0, 0), width=3)
    # Sign In
    draw_pre.rectangle([940, max(0, 8-Y_SHIFT), 1010, 38-Y_SHIFT], outline=(255, 0, 0), width=3)
    
    out_ws_pre = '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png'
    out_art_pre = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/executive-dashboard-pre.png'
    img_pre.save(out_ws_pre)
    img_pre.save(out_art_pre)

process()
print("Shifted Y coordinates up by 12 pixels.")

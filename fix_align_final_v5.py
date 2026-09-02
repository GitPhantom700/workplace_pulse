from PIL import Image, ImageDraw

def process():
    Y_SHIFT = 12
    # Shift circle to the right
    X_SHIFT_CIRCLE = 20
    
    # 1. Post-Login
    post_path = '/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png'
    img = Image.open(post_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Redact profile
    # Avatar: move to right by X_SHIFT_CIRCLE
    draw.ellipse([812 + X_SHIFT_CIRCLE, max(0, 10-Y_SHIFT), 838 + X_SHIFT_CIRCLE, 36-Y_SHIFT], fill=(200, 200, 200))
    # Name + Email
    draw.rectangle([845, max(0, 14-Y_SHIFT), 955, 23-Y_SHIFT], fill=(220, 220, 220))
    draw.rectangle([845, max(0, 25-Y_SHIFT), 975, 31-Y_SHIFT], fill=(230, 230, 230)) # Made email box slightly wider just in case
    
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
    
process()
print("Shifted circle to the right by 20 pixels.")

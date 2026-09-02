from PIL import Image, ImageDraw

def process(img_path, out_path, is_post_login):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    pixels = img.load()
    
    # We want to find the exact bounding boxes of the white pills in the top nav.
    # The top nav is roughly y = 0 to 50, x = 600 to 1024.
    # Background is (248, 250, 252) or (249,250,251). White is >250, >250, >250.
    
    # 1. Find all white pixels
    white_pixels = []
    for y in range(5, 45):
        for x in range(700, w-10):
            r, g, b = pixels[x, y]
            if r > 250 and g > 250 and b > 250:
                white_pixels.append((x, y))
                
    # 2. Cluster white pixels into connected components (pills)
    clusters = [] # list of lists of (x,y)
    for px, py in white_pixels:
        added = False
        for cluster in clusters:
            # If close to any pixel in cluster
            for cx, cy in cluster:
                if abs(cx - px) < 5 and abs(cy - py) < 5:
                    cluster.append((px, py))
                    added = True
                    break
            if added:
                break
        if not added:
            clusters.append([(px, py)])
            
    # merge overlapping clusters
    merged = True
    while merged:
        merged = False
        for i in range(len(clusters)):
            for j in range(i+1, len(clusters)):
                # check if bounds overlap or are close
                min_x1 = min(p[0] for p in clusters[i])
                max_x1 = max(p[0] for p in clusters[i])
                min_x2 = min(p[0] for p in clusters[j])
                max_x2 = max(p[0] for p in clusters[j])
                if not (max_x1 < min_x2 - 5 or max_x2 < min_x1 - 5): # x-overlap
                    clusters[i].extend(clusters[j])
                    clusters.pop(j)
                    merged = True
                    break
            if merged: break

    # sort clusters by x
    bounds = []
    for cluster in clusters:
        min_x = min(p[0] for p in cluster)
        max_x = max(p[0] for p in cluster)
        min_y = min(p[1] for p in cluster)
        max_y = max(p[1] for p in cluster)
        if max_x - min_x > 30 and max_y - min_y > 10:
            bounds.append((min_x, min_y, max_x, max_y))
            
    bounds.sort(key=lambda b: b[0])
    
    draw = ImageDraw.Draw(img)
    print(f"Found {len(bounds)} pills: {bounds}")
    
    if is_post_login:
        # Expected pills: [Webhooks, Demo Mode OFF, Profile]
        # Profile might not be a pure white pill if the avatar breaks it.
        # Let's just use the bounds directly.
        if len(bounds) >= 3:
            demo_box = bounds[-2] # Second to last
            prof_box = bounds[-1] # Last
            
            draw.rectangle(demo_box, outline=(255, 0, 0), width=2)
            draw.rectangle(prof_box, outline=(255, 0, 0), width=2)
            
            # redact inside prof_box
            min_x, min_y, max_x, max_y = prof_box
            # avatar is on the left of prof box
            draw.ellipse([min_x+2, min_y+2, min_x+32, min_y+32], fill=(200, 200, 200))
            draw.rectangle([min_x+40, min_y+5, max_x-5, min_y+15], fill=(220, 220, 220))
            draw.rectangle([min_x+40, max_y-15, max_x-15, max_y-5], fill=(230, 230, 230))
    else:
        # Pre-login
        # Expected pills: [Webhooks, Demo Mode ON, Sign In]
        if len(bounds) >= 3:
            demo_box = bounds[-2]
            signin_box = bounds[-1]
            draw.rectangle(demo_box, outline=(255, 0, 0), width=2)
            draw.rectangle(signin_box, outline=(255, 0, 0), width=2)

    img.save(out_path)
    img.save(out_path.replace('/assets/screenshots/', '/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/'))

process('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png',
        '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-post.png',
        True)
process('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png',
        '/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png',
        False)

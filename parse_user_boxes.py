from PIL import Image

def get_red_boxes(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    red_x = []
    for y in range(h):
        for x in range(w):
            r, g, b = img.getpixel((x, y))
            if r > 200 and g < 50 and b < 50:
                red_x.append(x)
    
    if not red_x:
        return []
        
    clusters = []
    current_cluster = [red_x[0]]
    for x in sorted(set(red_x)):
        if x - current_cluster[-1] > 20:
            clusters.append((current_cluster[0], current_cluster[-1]))
            current_cluster = [x]
        else:
            current_cluster.append(x)
    clusters.append((current_cluster[0], current_cluster[-1]))
    return clusters

print("Pre-Login Red Boxes in Crop:")
print(get_red_boxes('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322729049.png'))

print("Post-Login Red Boxes in Crop:")
print(get_red_boxes('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322715471.png'))

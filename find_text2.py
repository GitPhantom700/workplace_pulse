from PIL import Image
def scan(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    pixels = img.load()
    dark_x = []
    for y in range(15, 30):
        for x in range(600, w-20):
            r, g, b = pixels[x, y]
            # text-gray-700 or text-gray-500 is around 50 to 120
            # Also "Sign In" might be text-gray-700
            if r < 140 and g < 140 and b < 140 and r > 30 and g > 30 and b > 30:
                dark_x.append(x)
    
    # cluster them
    clusters = []
    if not dark_x: return
    current_cluster = [dark_x[0]]
    for x in sorted(set(dark_x)):
        if x - current_cluster[-1] > 30: # new cluster
            clusters.append((current_cluster[0], current_cluster[-1]))
            current_cluster = [x]
        else:
            current_cluster.append(x)
    clusters.append((current_cluster[0], current_cluster[-1]))
    print(clusters)

print("Pre-Login Gray Text Clusters:")
scan('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png')
print("Post-Login Gray Text Clusters:")
scan('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png')

from PIL import Image
def scan(img_path):
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    pixels = img.load()
    dark_x = []
    for y in range(15, 30):
        for x in range(600, w-20):
            r, g, b = pixels[x, y]
            if r < 80 and g < 80 and b < 80:
                dark_x.append(x)
    
    # cluster them
    clusters = []
    if not dark_x: return
    current_cluster = [dark_x[0]]
    for x in sorted(set(dark_x)):
        if x - current_cluster[-1] > 20: # new cluster
            clusters.append((current_cluster[0], current_cluster[-1]))
            current_cluster = [x]
        else:
            current_cluster.append(x)
    clusters.append((current_cluster[0], current_cluster[-1]))
    print(clusters)

print("Pre-Login Dark Text Clusters:")
scan('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png')
print("Post-Login Dark Text Clusters:")
scan('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322360451.png')

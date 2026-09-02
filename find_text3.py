from PIL import Image
img = Image.open('/Users/chandrahin/.gemini/antigravity/brain/673d00df-4447-454a-9ef5-11112f2ddbf4/.user_uploaded/media_1788322473314.png').convert('RGB')
w, h = img.size
pixels = img.load()
dark_x = []
for y in range(15, 30):
    for x in range(600, w-10):
        r, g, b = pixels[x, y]
        if r < 180 and g < 180 and b < 180:
            dark_x.append(x)
            
clusters = []
if dark_x:
    current_cluster = [dark_x[0]]
    for x in sorted(set(dark_x)):
        if x - current_cluster[-1] > 30:
            clusters.append((current_cluster[0], current_cluster[-1]))
            current_cluster = [x]
        else:
            current_cluster.append(x)
    clusters.append((current_cluster[0], current_cluster[-1]))
print(clusters)

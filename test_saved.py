from PIL import Image

def draw_ascii(path, w_max=120):
    img = Image.open(path).convert('RGB')
    w, h = img.size
    
    # Crop the relevant part x=700-1024, y=0-50
    img = img.crop((700, 0, 1024, 50))
    w, h = img.size
    
    ratio = w / w_max
    new_h = int(h / ratio)
    img = img.resize((w_max, new_h))
    
    for y in range(new_h):
        line = ""
        for x in range(w_max):
            r, g, b = img.getpixel((x, y))
            if r > 150 and g < 100 and b < 100:
                line += "R" # Red box
            elif r < 140 and g < 140 and b < 140 and r > 30:
                line += "T" # Text/Dark
            else:
                line += "."
        print(line)

print("Saved Pre-Login:")
draw_ascii('/Users/chandrahin/Desktop/google_projects/workplace_pulse/assets/screenshots/executive-dashboard-pre.png', 100)

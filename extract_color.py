from PIL import Image
from collections import Counter

def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        img = img.resize((50, 50))  # Resize for speed
        pixels = list(img.getdata())
        # Remove transparent pixels if any
        if img.mode == 'RGBA':
            pixels = [x[:3] for x in pixels if x[3] > 0]
        
        # Get most common color
        counts = Counter(pixels)
        most_common = counts.most_common(1)[0][0]
        return '#{:02x}{:02x}{:02x}'.format(*most_common)
    except Exception as e:
        print(f"Error: {e}")
        return None

color = get_dominant_color("frontend/img/logo.jpg")
print(f"DOMINANT_COLOR:{color}")

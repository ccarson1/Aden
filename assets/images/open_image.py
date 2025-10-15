from PIL import Image
img = Image.open("mountain.jpg").convert("RGB")
img.save("mountain_fixed.png")
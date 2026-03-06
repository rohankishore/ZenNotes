from PIL import Image

# Open the PNG image
img = Image.open("icon.png")

# Convert and save as ICO
img.save("icon.ico", format="ICO")

print("icon.png successfully converted to icon.ico")

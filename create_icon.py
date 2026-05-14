from PIL import Image, ImageDraw

# Create a 64x64 icon
img = Image.new('RGB', (64, 64), color='white')
draw = ImageDraw.Draw(img)

# Draw a simple clock icon
draw.ellipse([8, 8, 56, 56], outline='black', width=3)
draw.line([32, 32, 32, 16], fill='black', width=3)  # Hour hand
draw.line([32, 32, 44, 32], fill='black', width=3)  # Minute hand

# Save as PNG
img.save('icon.png')
print("Icon created: icon.png")
from PIL import Image
import sys
import os

# configs
IMAGE_PATH = sys.argv[1] if len(sys.argv) > 1 else 'image.jpg'
LED_MATRIX_WIDTH = 32
LED_MATRIX_HEIGHT = 32
# end configs

# output path
OUTPUT_PATH = os.path.splitext(IMAGE_PATH)[0] + '.bmp'
# end output path

# open image
image = Image.open(IMAGE_PATH)

# get original dimensions
width, height = image.size

# crop to center square using the smallest dimension
min_dimension = min(width, height)
left = (width - min_dimension) // 2
top = (height - min_dimension) // 2
right = left + min_dimension
bottom = top + min_dimension

# crop the image to the center square
image = image.crop((left, top, right, bottom))

# resize image to match LED matrix resolution
image = image.resize((LED_MATRIX_WIDTH, LED_MATRIX_HEIGHT))

# Convert and save as BMP
image.save(OUTPUT_PATH, format='BMP')

print("Image converted to BMP successfully!")

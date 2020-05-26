from PIL import Image, ImageDraw
from numpy import *

# Ideas:
'''
1. Convert all images in directory that do not have NAME_mozzified.EXTENSION counterpart.
2. Config file with settings:
  2.A. Image dimensions -- number of x and y squares
  2.B. Image dimensions -- matching aspect ratio
  2.C. Image spacing -- spacing between squares
  2.D. Image display -- square size
3. Squares have an extra element: a border with potentially a different color.
'''

# Config
MOZ_SQUARE_SIZE = 16
MOZ_SQUARE_SPACING = int(MOZ_SQUARE_SIZE / 4)

MOZ_SQUARES_X, MOZ_SQUARES_Y = 15, 15

CANVAS_X = (MOZ_SQUARES_X + 1)*MOZ_SQUARE_SPACING + MOZ_SQUARES_X*MOZ_SQUARE_SIZE
CANVAS_Y = (MOZ_SQUARES_Y + 1)*MOZ_SQUARE_SPACING + MOZ_SQUARES_Y*MOZ_SQUARE_SIZE

INPUT_FILE = "input.png"
INPUT_FILE_NAME = INPUT_FILE.split('.')[0]
INPUT_FILE_EXTENSION = '.' + INPUT_FILE.split('.')[1]

# Input and image data setup
im = Image.open(INPUT_FILE)
im = im.copy()

_, _, im_dimensions_x, im_dimensions_y = im.getbbox()

im_dimensions_diff = im_dimensions_x - im_dimensions_y \
  if im_dimensions_x > im_dimensions_y else im_dimensions_y - im_dimensions_x

im_crop_offset = int(im_dimensions_diff / 2)

if im_dimensions_x > im_dimensions_y:
  im_cropped_x_left = im_crop_offset
  im_cropped_x_right = im_dimensions_x - im_crop_offset

  im_cropped_y_upper = 0
  im_cropped_y_lower = im_dimensions_y
else:  # im_dimensions_x <= im_dimensions_y
  im_cropped_x_left = 0
  im_cropped_x_right = im_dimensions_x

  im_cropped_y_upper = im_crop_offset
  im_cropped_y_lower = im_dimensions_y - im_crop_offset

# DEBUG
print("Will crop to: {} {} {} {}".format(im_cropped_x_left, im_cropped_y_upper, im_cropped_x_right, im_cropped_y_lower))


# Pre-processing
# Assuming we are outputting a square...
# Crop square to center.
im_cropped = im.crop((im_cropped_x_left, im_cropped_y_upper, im_cropped_x_right, im_cropped_y_lower))
# im_cropped.save(INPUT_FILE_NAME + "_crop" + INPUT_FILE_EXTENSION)  # DEBUG

# Convert image to numpy array
im_array = asarray(im_cropped)
# print(type(im_array))  # DEBUG

# DEBUG
# summarize image details
# print(im_array)
# print(im_array.shape)
# print(im_array.mean)
# print(im_array.size)

im_average_color = tuple(map(int, mean(im_array, axis=(0, 1))))
print("Average color:", im_average_color)


# Draw
im_pixelified = Image.new('RGB', (CANVAS_X, CANVAS_Y), im_average_color)
draw = ImageDraw.Draw(im_pixelified)

_, _, im_cropped_dimensions_x, im_cropped_dimensions_y = im_cropped.getbbox()
MOZ_chunk_x = int(im_cropped_dimensions_x / MOZ_SQUARES_X)
MOZ_chunk_y = int(im_cropped_dimensions_y / MOZ_SQUARES_Y)

for x in range(MOZ_SQUARES_X):
  for y in range(MOZ_SQUARES_Y):
    # Find next chunk
    MOZ_next_chunk_x_left = x*MOZ_chunk_x
    MOZ_next_chunk_x_right = x*MOZ_chunk_x + MOZ_chunk_x
    MOZ_next_chunk_y_upper = y * MOZ_chunk_y
    MOZ_next_chunk_y_lower = y * MOZ_chunk_y + MOZ_chunk_y

    # Find average color of respective chunk
    im_chunk = im_cropped.crop((MOZ_next_chunk_x_left, MOZ_next_chunk_y_upper, MOZ_next_chunk_x_right, MOZ_next_chunk_y_lower))
    # im_chunk.save(INPUT_FILE_NAME + "_chunk_" + str(x) + "_" + str(y) + INPUT_FILE_EXTENSION)  # DEBUG

    # Convert image to numpy array
    im_chunk_array = asarray(im_chunk)
    # print(type(im_chunk_array))  # DEBUG

    im_chunk_average_color = tuple(map(int, mean(im_chunk_array, axis=(0, 1))))

    # Color it in
    draw.rectangle(
      ((x + 1)*MOZ_SQUARE_SPACING + x*MOZ_SQUARE_SIZE,
       (y + 1)*MOZ_SQUARE_SPACING + y*MOZ_SQUARE_SIZE,
       (x + 1)*MOZ_SQUARE_SPACING + (x + 1)*MOZ_SQUARE_SIZE - 1,
       (y + 1)*MOZ_SQUARE_SPACING + (y + 1)*MOZ_SQUARE_SIZE - 1),
      fill=im_chunk_average_color,
      outline=im_chunk_average_color,
      width=0)

im_pixelified.save(INPUT_FILE_NAME + "_mozzified" + INPUT_FILE_EXTENSION, quality=95)

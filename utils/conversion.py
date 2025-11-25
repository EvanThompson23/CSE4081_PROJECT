from PIL import Image
import numpy as np


def image_to_array(path):
    img = Image.open(path).convert("RGBA")  # Standardize format
    arr = np.array(img)
    return arr


def array_to_image(arr, path):
    img = Image.fromarray(arr.astype("uint8"), "RGBA")
    img.save("imgtest.png")



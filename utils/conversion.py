from PIL import Image
import numpy as np


def image_to_array(path):
    img = Image.open(path).convert("RGBA")  # Standardize format
    arr = np.array(img)
    return arr


def array_to_image(arr, path):
    """
    Save an RGBA numpy array as a PNG image.

    Parameters
    ----------
    arr : np.ndarray
        Image data, shape (H, W, 4), dtype uint8 or convertible to uint8.
    path : str
        Output file path. If empty, defaults to 'imgtest.png'.
    """
    img = Image.fromarray(arr.astype("uint8"), "RGBA")

    if not path:
        path = "imgtest.png"

    # Always save as PNG for decompression output
    img.save(path, format="PNG")



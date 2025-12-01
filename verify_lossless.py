from utils import conversion
import numpy as np
import os
import sys


def verify_lossless(original_path: str = "1.png", reconstructed_path: str = "decompressed.png") -> None:
    """
    Load the original PNG and the decompressed PNG, and verify that
    the codec is lossless by comparing pixel arrays.
    """
    if not os.path.exists(original_path):
        print(f"Original file not found: {original_path}")
        return
    if not os.path.exists(reconstructed_path):
        print(f"Reconstructed file not found: {reconstructed_path}")
        return

    orig = conversion.image_to_array(original_path)
    rec = conversion.image_to_array(reconstructed_path)

    same_shape = orig.shape == rec.shape
    print(f"Same shape: {same_shape} (orig={orig.shape}, rec={rec.shape})")

    if not same_shape:
        print("Shapes differ; images are not identical.")
        return

    equal = np.array_equal(orig, rec)
    max_abs_diff = np.max(np.abs(orig.astype(np.int16) - rec.astype(np.int16)))

    print(f"Exactly equal: {equal}")
    print(f"Max per-channel absolute difference: {max_abs_diff}")

    if equal:
        print("Result: The codec is lossless for this image (pixel-perfect match).")
    else:
        print("Result: The codec is NOT perfectly lossless for this image.")


def main():
    # sys.argv[1] = original image (optional), sys.argv[2] = reconstructed image (optional)
    if len(sys.argv) > 1:
        original_path = sys.argv[1]
    else:
        original_path = "1.png"

    if len(sys.argv) > 2:
        reconstructed_path = sys.argv[2]
    else:
        reconstructed_path = "decompressed.png"

    verify_lossless(original_path, reconstructed_path)


if __name__ == "__main__":
    main()



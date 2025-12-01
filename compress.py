from utils import color_alterations
from utils import conversion
from utils import predictor
from utils import lz77
import numpy as np
import os
import sys


def main():
    # Use first CLI arg as input path if provided, else default to "1.png"
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        input_path = "1.png"

    image_array = conversion.image_to_array(input_path)

    AR = 0
    AB = 0
    transformed = color_alterations.color_decorrel(image_array, AR=AR, AB=AB)
    transformed = color_alterations.subtract_green(transformed)

    residuals, block_modes = predictor.encode_predictor(transformed)

    indices, palette = color_alterations.palette(residuals)

    if indices is not None and palette is not None:
        use_palette = np.array([1], dtype=np.uint8)
        data_for_lz = np.stack([indices] * 4, axis=-1).astype(np.int16)
    else:
        use_palette = np.array([0], dtype=np.uint8)
        palette = np.empty((0,), dtype=np.uint8)
        data_for_lz = residuals

    height, width, channels = data_for_lz.shape
    encoded, row_num = lz77.lzComp(data_for_lz)

    v_blocks, h_blocks = block_modes.shape
    use_palette_flag = int(use_palette[0])

    offsets = np.array([int(o) for (o, _, _) in encoded], dtype=np.uint32)
    lengths = np.array([int(l) for (_, l, _) in encoded], dtype=np.uint32)
    has_symbol = np.ones(len(encoded), dtype=np.uint8)
    symbols = np.array([int(t) for (_, _, t) in encoded], dtype=np.uint8)

    np.savez_compressed(
        "compressed.npz",
        use_palette_flag=use_palette_flag,
        palette=palette,
        block_modes=block_modes.astype(np.uint8),
        height=height,
        width=width,
        channels=channels,
        offsets=offsets,
        lengths=lengths,
        has_symbol=has_symbol,
        symbols=symbols,
    )

    compressed_size = os.path.getsize("compressed.npz")
    raw_pixel_size = image_array.nbytes  # bytes of RGBA pixel data in memory

    if compressed_size > 0:
        compression_ratio = raw_pixel_size / compressed_size
    else:
        compression_ratio = float("inf")

    print(f"Input image: {input_path}")
    print(f"Raw RGBA pixel data (in memory): {raw_pixel_size} bytes")
    print(f"Compressed container (compressed.npz): {compressed_size} bytes")
    print(f"Compression ratio (raw_pixels / compressed): {compression_ratio:.2f}")


if __name__ == "__main__":
    main()
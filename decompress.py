from utils import color_alterations
from utils import conversion
from utils import predictor
from utils import lz77
import numpy as np
import os


if __name__ == "__main__":

    data = np.load("compressed.npz")

    use_palette_flag = int(data["use_palette_flag"])
    palette = data["palette"]
    block_modes = data["block_modes"].astype(np.uint8)

    height = int(data["height"])
    width = int(data["width"])
    channels = int(data["channels"])

    offsets = data["offsets"]
    lengths = data["lengths"]
    has_symbol = data["has_symbol"]
    symbols = data["symbols"]

    encoded = []
    for o, l, hs, sym in zip(offsets, lengths, has_symbol, symbols):
        term = int(sym)
        encoded.append((int(o), int(l), term))

    transformed = lz77.lzDecode_from_encoded(
        encoded,
        height,
        width,
        channels,
        dtype=np.int16,
    )

    if use_palette_flag == 1 and palette is not None:
        indices = transformed[:, :, 0].astype(np.int64)
        after_palette = color_alterations.depalette(indices, palette)
    else:
        after_palette = transformed

    reconstructed_transformed = predictor.decode_predictor(after_palette, block_modes)

    AR = 0
    AB = 0
    after_color = color_alterations.add_green(reconstructed_transformed)
    image_array = color_alterations.color_recorrel(after_color, AR=AR, AB=AB)

    output_path = "decompressed.png"
    conversion.array_to_image(image_array, output_path)

    compressed_size = os.path.getsize("compressed.npz")
    decompressed_size = os.path.getsize(output_path)

    print(f"Compressed container (compressed.npz): {compressed_size} bytes")
    print(f"Decompressed PNG ({output_path}): {decompressed_size} bytes")
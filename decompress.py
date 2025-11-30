from utils import color_alterations
from utils import conversion
from utils import predictor
from utils import lz77

if __name__ == "__main__":

    file = "encoded_LZ77.enc"

    image_array = lz77.lzDecode(file)

    #uncompressed = color_alterations.color_decache(stream, height, width)
    image_array = color_alterations.add_green(image_array)
    image_array = color_alterations.color_recorrel(image_array)

    conversion.array_to_image(image_array, "")
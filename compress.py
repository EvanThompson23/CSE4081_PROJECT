from utils import color_alterations
from utils import conversion
from utils import predictor
from utils import lz77

if __name__ == "__main__":
    path_to_file = "C:/Users/sothi/Pictures/ebx3u9ub1yq51.png"
    image_array = conversion.image_to_array(path_to_file)

    #res, block_modes = predictor.encode_predictor(image_array)

    image_array = color_alterations.color_decorrel(image_array)
    image_array = color_alterations.subtract_green(image_array)

    #indice, pallette = color_alterations.palette(image_array_de_color)
    #stream, height, width = color_alterations.color_cache(image_array_de_color)

    lz77.lzComp(image_array)
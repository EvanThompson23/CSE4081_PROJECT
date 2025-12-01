import numpy as np


# Compress
def subtract_green(image_array):
    out = image_array.astype(np.int16).copy()

    R = out[:, :, 0]
    G = out[:, :, 1]
    B = out[:, :, 2]

    R -= G
    B -= G

    out[:, :, 0] = R
    out[:, :, 2] = B

    return out


# Decompress
def add_green(transformed):
    arr = transformed.astype(np.int16).copy()

    R = arr[:, :, 0]
    G = arr[:, :, 1]
    B = arr[:, :, 2]

    R += G
    B += G
    
    arr[:, :, 0] = R
    arr[:, :, 2] = B

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return arr


# compress
def color_decorrel(image_array, AR=0, AB=0):
    block_size = 16
    height, width, channel = image_array.shape
    img = image_array.astype(np.int16)
    out = img.copy()

    for by in range(0, height, block_size):
        by1 = min(by + block_size, height)
        for bx in range(0, width, block_size):
            bx1 = min(bx + block_size, width)
            G = img[by:by1, bx:bx1, 1].astype(np.int32)

            if channel >= 3:
                R = img[by:by1, bx:bx1, 0].astype(np.int32)
                B = img[by:by1, bx:bx1, 2].astype(np.int32)

                R2 = R - ((G * AR) >> 5)
                B2 = B - ((G * AB) >> 5)

                out[by:by1, bx:bx1, 0] = R2
                out[by:by1, bx:bx1, 2] = B2
    return out


# decompress
def color_recorrel(transformed, AR=0, AB=0):
    block_size = 16
    height, width, channel = transformed.shape
    out = transformed.astype(np.int32).copy()

    # Goes through blocks of 16/16
    for by in range(0, height, block_size):
        by1 = min(by + block_size, height)
        for bx in range(0, width, block_size):
            bx1 = min(bx + block_size, width)
            G = out[by:by1, bx:bx1, 1]

            if channel >= 3:
                Rprime = out[by:by1, bx:bx1, 0]
                Bprime = out[by:by1, bx:bx1, 2]

                R = Rprime + ((G * AR) >> 5)
                B = Bprime + ((G * AB) >> 5)

                out[by:by1, bx:bx1, 0] = R
                out[by:by1, bx:bx1, 2] = B
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out
    

# compress
def palette(image_array):
    max_palette_size=256

    height, width, channel = image_array.shape
    flat = image_array.reshape(-1, channel)

    dt = np.dtype((np.void, flat.dtype.itemsize * flat.shape[1]))
    flat_view = np.ascontiguousarray(flat).view(dt).ravel()
    unique_view, inv = np.unique(flat_view, return_inverse=True)
    num_unique = unique_view.shape[0]
    if num_unique > max_palette_size:
        return None, None

    palette = np.asarray([np.frombuffer(v.tobytes(), dtype=flat.dtype) for v in unique_view], dtype=np.uint8)
    indices = inv.reshape(height, width)

    if num_unique <= 256:
        indices = indices.astype(np.uint8)
    else:
        indices = indices.astype(np.uint16)
        
    return indices, palette


# decompress
def depalette(indices, palette):
    height, width  = indices.shape
    channel = palette.shape[1]

    out = np.zeros((height, width, channel), dtype=np.uint8)
    for c in range(channel):
        out[:, :, c] = palette[indices, c]
    return out


# compress
def color_hash(r, g, b, a, cache_size):
    return (r * 3 + g * 5 + b * 7 + a * 11) % cache_size

def color_cache(image_array):
    cache_size = 64
    height, width, channel = image_array.shape
    has_alpha = (channel == 4)
    cache = [None] * cache_size
    
    stream = []
    for y in range(height):
        for x in range(width):
            if has_alpha:
                r, g, b, a = map(int, image_array[y, x, :4])
            else:
                r, g, b = map(int, image_array[y, x, :3])
                a = 255
            h = color_hash(r, g, b, a, cache_size)
            entry = cache[h]
            
            if (
                entry is not None and 
                entry[0] == r and 
                entry[1] == g and 
                entry[2] == b and 
                entry[3] == a
                ):
                stream.append(('HIT', h))
            else:
                stream.append(('MISS', (r, g, b, a)))
                cache[h] = (r, g, b, a)

    return stream, height, width


# decompress
def color_decache(stream, height, width):
    cache_size = 64
    has_alpha = False
    cache = [None] * cache_size
    if has_alpha:
        channel = 4
    else:
        channel = 3
    out = np.zeros((height, width, channel), dtype=np.uint8)
    idx = 0
    for y in range(height):
        for x in range(width):
            tag, val = stream[idx]
            idx += 1
            if tag == 'HIT':
                h = val
                r, g, b, a = cache[h]
            else:
                r, g, b, a = val
                h = color_hash(r, g, b, a, cache_size)
                cache[h] = (r, g, b, a)
            if has_alpha:
                out[y, x, :] = (r, g, b, a)
            else:
                out[y, x, :3] = (r, g, b)
    return out

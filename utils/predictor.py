import numpy as np


def paeth(left, top, top_left):
    p = left + top - top_left
    pa = abs(p - left)
    pb = abs(p - top)
    pc = abs(p - top_left)
    if pa <= pb and pa <= pc:
        return left
    elif pb <= pc:
        return top
    else:
        return top_left


def clamp(value):
    return max(0, min(255, value))


def get_predictor_value(mode, left, top, top_left, top_right):
    if mode == 0:
        return 0
    elif mode == 1:
        return left
    elif mode == 2:
        return top
    elif mode == 3:
        return (left + top) >> 1
    elif mode == 4:
        return paeth(left, top, top_left)
    elif mode == 5:
        return clamp(left + top - top_left)
    elif mode == 6:
        return clamp(left + top - top_right)
    elif mode == 7:
        return clamp(left - top + top_left)
    elif mode == 8:
        return clamp(top - left + top_right)
    elif mode == 9:
        if abs(left - top_left) < abs(top - top_left):
            return left
        return top
    elif mode == 10:
        if abs(left - top) <= abs(top_left - top):
            return left
        return top_left
    elif mode == 11:
        if abs(top - top_left) <= abs(top_left - left):
            return top
        return top_left
    elif mode == 12:
        return (top + top_right) >> 1
    else:
        return None
        

def get_neighbor_pixels(image_channel, row, col):
    if col > 0: 
        left = int(image_channel[row, col-1]) 
    else: 
        left = 0

    if row > 0:
        top = int(image_channel[row-1, col]) 
    else:
        top = 0

    if row > 0 and col > 0:
        top_left = int(image_channel[row-1, col-1]) 
    else:
        top_left = 0

    if row > 0 and col+1 < image_channel.shape[1]: 
        top_right = int(image_channel[row-1, col+1]) 
    else:
        top_right = 0 

    return left, top, top_left, top_right
    

def encode_predictor(array):
    block_size = 16
    modes = 13

    if array.ndim == 2:
        height, width = array.shape
        channels = 1
        image = array.reshape((height, width, channels))
    else:
        height, width, channels = array.shape
        image = array

    v_blocks = (height + block_size - 1) // block_size
    h_blocks = (width + block_size - 1) // block_size
    block_modes = np.zeros((v_blocks, h_blocks), dtype=np.uint8)

    residuals = np.zeros_like(image, dtype=np.int16)

    # running reconstructed image buffer that encoder maintains
    reconstructed = np.zeros((height, width, channels), dtype=np.int32)

    for row in range(v_blocks):
        s_row = row * block_size
        e_row = min(s_row + block_size, height)

        for column in range(h_blocks):
            s_column = column * block_size
            e_column = min(s_column + block_size, width)

            best_mode = 0
            best_score = None

            # evaluate each mode by simulating encoding into a temp reconstructed buffer
            for mode in range(modes):
                score = 0
                temp_recon = reconstructed.copy()

                for hold_row in range(s_row, e_row):
                    for hold_col in range(s_column, e_column):
                        for hold_channel in range(channels):
                            channel_data = image[:, :, hold_channel]

                            if hold_col > 0:
                                left = int(temp_recon[hold_row, hold_col-1, hold_channel]) 
                            else: 
                                left = 0

                            if hold_row > 0:
                                top = int(temp_recon[hold_row-1, hold_col, hold_channel]) 
                            else: 
                                top = 0

                            if hold_row > 0 and hold_col > 0:
                                top_left = int(temp_recon[hold_row-1, hold_col-1, hold_channel]) 
                            else:
                                top_left = 0

                            if hold_row > 0 and hold_col+1 < width:
                                top_right = int(temp_recon[hold_row-1, hold_col+1, hold_channel]) 
                            else:
                                top_right = 0

                            predicted = get_predictor_value(mode, left, top, top_left, top_right)
                            original_value = int(channel_data[hold_row, hold_col])
                            resid = original_value - predicted
                            score += abs(resid)

                            # simulate writing reconstructed pixel so future predictions use it
                            temp_recon[hold_row, hold_col, hold_channel] = predicted + resid

                            if best_score is not None and score > best_score:
                                break
                        if best_score is not None and score > best_score:
                            break
                    if best_score is not None and score > best_score:
                        break

                if best_score is None or score < best_score:
                    best_score = score
                    best_mode = mode

            block_modes[row, column] = best_mode

            # now encode for real into residuals and update the running reconstructed buffer
            for hold_row in range(s_row, e_row):
                for hold_col in range(s_column, e_column):
                    for hold_channel in range(channels):
                        channel_data = image[:, :, hold_channel]

                        if hold_col > 0: 
                            left = int(reconstructed[hold_row, hold_col-1, hold_channel]) 
                        else:
                            left = 0

                        if hold_row > 0:
                            top = int(reconstructed[hold_row-1, hold_col, hold_channel]) 
                        else:
                            top = 0

                        if hold_row > 0 and hold_col > 0: 
                            top_left = int(reconstructed[hold_row-1, hold_col-1, hold_channel]) 
                        else:
                            top_left = 0

                        if hold_row > 0 and hold_col+1 < width:
                            top_right = int(reconstructed[hold_row-1, hold_col+1, hold_channel]) 
                        else:
                            top_right = 0

                        predicted = get_predictor_value(best_mode, left, top, top_left, top_right)
                        original_value = int(channel_data[hold_row, hold_col])
                        resid = original_value - predicted
                        residuals[hold_row, hold_col, hold_channel] = resid

                        reconstructed[hold_row, hold_col, hold_channel] = predicted + resid

    if residuals.shape[2] == 1:
        residuals = residuals[:, :, 0]

    return residuals, block_modes
            

def decode_predictor(residual_image, prediction_mode_map):
    block_size = 16

    image_height, image_width, num_channels = residual_image.shape
    # use int32 internally to avoid overflow warnings when adding residuals
    reconstructed_image = np.zeros(
        (image_height, image_width, num_channels),
        dtype=np.int32,
    )

    for block_row in range(0, image_height, block_size):
        for block_col in range(0, image_width, block_size):

            current_mode = prediction_mode_map[
                block_row // block_size,
                block_col // block_size
            ]

            # decode pixels inside this block
            for row in range(block_row, min(block_row + block_size, image_height)):
                for col in range(block_col, min(block_col + block_size, image_width)):

                    for channel in range(num_channels):

                        # get *already reconstructed* neighbors
                        left_value, top_value, top_left_value, top_right_value = get_neighbor_pixels(
                            reconstructed_image[:, :, channel],
                            row,
                            col
                        )

                        # use your encoder's predictor function
                        predicted_pixel = get_predictor_value(
                            current_mode,
                            left_value,
                            top_value,
                            top_left_value,
                            top_right_value
                        )

                        # reconstruct pixel: predicted + residual
                        reconstructed_image[row, col, channel] = int(
                            predicted_pixel
                        ) + int(residual_image[row, col, channel])

    # return as int16 to match encoder's residual type; later stages clip to uint8
    return reconstructed_image.astype(np.int16)

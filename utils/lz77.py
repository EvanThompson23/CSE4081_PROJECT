import conversion
import numpy as np
import math

def find_offset(search_buffer_list, term):
    parse_string = "".join(search_buffer_list)

    if parse_string.find(term) == -1:
        return -1

    offset = len(search_buffer_list) - parse_string.rfind(term) - 1
        
    return offset + 1


def lzComp(path):
    bit_stream = conversion.image_to_array(path)

    bit_stream, row_num = create_bit_string(bit_stream)

    search_buffer = math.floor(row_num/2)
    look_buffer = math.floor(row_num/2)
    
    encode = [(0 ,0 ,bit_stream[0])]
    count = 1
    length = 1

    while (count < len(bit_stream)):
        current_bit = bit_stream[count]

        lower_bound_window = count - search_buffer
        upper_bound_window = count + look_buffer

        if lower_bound_window < 0:
            lower_bound_window = 0

        if upper_bound_window > len(bit_stream):
            upper_bound_window = len(bit_stream) 

        search_window = bit_stream[lower_bound_window:count]

        if search_window.find(current_bit) == -1:
            encode.append((0, 0, current_bit))
        else:
            length = 1
            for i in range(count+1, upper_bound_window):
                temp_bit = current_bit + bit_stream[i]

                if search_window.find(temp_bit) > -1:
                    current_bit = temp_bit
                    length += 1
                else:
                    break
            
            offset = find_offset(search_window, current_bit)
            
            if count + length + 1 >= len(bit_stream):
                current_bit = ""
            else:
                current_bit = bit_stream[count + length]

            encode.append((offset, length, current_bit))

            count += length

        count += 1
        
    file_name = "encoded_LZ77.txt"

    with open(file_name, "w") as output:
        output.write(f"row_num={row_num}")
        for tup in encode:
            output.write(str(tup))


def lzDecode(file):
    decode_string = ""

    f = open(file)
    input_expr = f.read()
    input_expr = input_expr[input_expr.index("=")+1:]

    row_num = int(input_expr[:input_expr.index("(")])

    input_expr = input_expr[input_expr.index("(") + 1:]
    input_expr = input_expr.split(")")

    for tup in input_expr[:len(input_expr) - 1]:
        tup = tup.split(" ")
        offset, length, term = int(tup[0].strip("(, ")), int(tup[1].strip(", ")), tup[2]

        if term != "":
            term = term.strip("' ")

            if offset != 0 and length != 0:
                starting_index = len(decode_string) - offset
                insert_term = decode_string[starting_index:starting_index+length]

                if offset == length:
                    complete_insert_term = insert_term
                else:
                    complete_insert_term = insert_term*(math.floor(length/offset)) + insert_term[:length]

                decode_string = decode_string + complete_insert_term

        
            decode_string += term
        #print(decode_string)

    #print(decode_string)
    bit_array = create_bit_array(decode_string.split(","), row_num)

    return bit_array

    #print(bit_array)
        

def create_bit_string(bit_stream):
    bit_string = []
    row_num = len(bit_stream[0])

    for bit_set in bit_stream:
        for bit_long in bit_set:
            bit_string.append(str(bit_long[0]))
            bit_string.append(str(bit_long[1]))
            bit_string.append(str(bit_long[2]))
            bit_string.append(str(bit_long[3]))

    file_name = "uncompressed.txt"

    with open(file_name, "w") as output:
        for bit in bit_string:
            output.write(bit)

    return ",".join(bit_string), row_num

def create_bit_array(bit_string, row_num):
    bit_array = []
    row_holder = []
    temp_holder = []

    for bit in bit_string:    
        insert_bit = np.uint8(int(bit))
        temp_holder.append(insert_bit)

        if len(temp_holder) == 4:
            row_holder.append(temp_holder)
            temp_holder = []
        
        if len(row_holder) == row_num:
            bit_array.append(row_holder)
            row_holder = []

    return np.array(bit_array)
        

if __name__ == "__main__":

    path_to_file = "C:/Users/sothi/Pictures/GTNYTNsWoAAGeXm.jpg"

    lzComp(path_to_file)

    lzDecode("encoded_LZ77.txt")

    #bit_stream = conversion.image_to_array(path_to_file)

    #bits_to_encode, row_num = create_bit_string(bit_stream)

    #print(len(bits_to_encode))

    #bit_stream = create_bit_array(lzDecode(encoded), row_num)

    #conversion.array_to_image(bit_stream, "C:/Users/sothi/Documents/testOut")
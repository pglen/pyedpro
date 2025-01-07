def validUTF8(data):

    if data == []:
        return True

    binary_data = [bin(num)[2:].zfill(8) for num in data]

    # Check for Overlong Encodings
    if any(bin_num.startswith("0") for bin_num in binary_data):
        return False

    # Check for Invalid Continuation Bytes
    if any(not bin_num.startswith("10") for bin_num in binary_data[1:]):
        return False

    # Validate Code Point Ranges
    decoded_chars = [int(bin_num, 2) for bin_num in binary_data]
    if any(0xD800 <= code_point <= 0xDFFF for code_point in decoded_chars):
        return False

    # Handle Overlong Sequences
    decoded_str = "".join(chr(char) for char in decoded_chars)
    reencoded_data = decoded_str.encode("utf-8")
    if binary_data != [bin(byte)[2:].zfill(8) for byte in reencoded_data]:
        return False

    # Handle Maximum Code Point
    if any(code_point > 0x10FFFF for code_point in decoded_chars):
        return False

    # Validate Sequence Lengths
    expected_length = 0
    for i, bin_num in enumerate(binary_data):
        if i == 0:
            if bin_num.startswith("110"):
                expected_length = 2
            elif bin_num.startswith("1110"):
                expected_length = 3
            elif bin_num.startswith("11110"):
                expected_length = 4
            else:
                continue
        elif bin_num.startswith("10"):
            expected_length -= 1
        else:
            return False
    if expected_length > 0:
        return False

    return True

if __name__ == '__main__':

    strx = b"hello"

    #strx = b"Файловий менеджер Nautilus"
    strx=b"\x04\x39\u043b\u043e\u0432\u0438\u0439\u043c\u0435\u043d\u0435"
    print("decode", "'" +  strx.decode() + "'")
    ret = validUTF8(strx)
    print("utf", strx, ret)


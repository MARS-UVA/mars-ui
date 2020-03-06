def encode_values(left, right, act1, act2, ladder, dbin):
    value = (left & 0b11111100) >> 2
    value <<= 6
    value |= (right & 0b11111100) >> 2
    value <<= 6
    value |= (act1 & 0b11111100) >> 2
    value <<= 6
    value |= (act2 & 0b11111100) >> 2
    value <<= 6
    value |= (ladder & 0b11111100) >> 2
    value <<= 2
    value |= dbin
    return value
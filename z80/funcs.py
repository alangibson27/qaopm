def to_signed(val):
    if val & 0x80 != 0:
        return val - 256
    else:
        return val

def big_endian_value(little_endian_value):
    lsb = little_endian_value[0]
    msb = little_endian_value[1]
    return (msb << 8) + lsb

def bitwise_add(v1, v2):
    v1_low_nib = v1 & 0xf
    v2_low_nib = v2 & 0xf

    low_nib = v1_low_nib + v2_low_nib
    half_carry = low_nib > 0xf

    result = v1 + v2
    return result & 0xff, half_carry, result > 0xff

def bitwise_sub(v1, v2):
    v1_low_nib = v1 & 0xf
    v2_low_nib = v2 & 0xf

    low_nib = v1_low_nib - v2_low_nib
    half_borrow = low_nib < 0x00

    result = v1 - v2
    return result & 0xff, half_borrow, result < 0x00
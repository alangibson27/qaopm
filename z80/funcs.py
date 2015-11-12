def twos_complement(val):
    if val & 0x80 != 0:
        return val - 256
    else:
        return val


def big_endian_value(little_endian_value):
    lsb = little_endian_value[0]
    msb = little_endian_value[1]
    return (msb << 8) + lsb
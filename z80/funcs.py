def twos_complement(val):
    if val & 0x80 != 0:
        return val - 256
    else:
        return val

def big_endian_value(msb, lsb):
    return (msb << 8) + lsb
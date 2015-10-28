def twos_complement(val):
    if val & 0x80 != 0:
        return val - 256
    else:
        return val
import argparse
from spectrum.computer import start

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('rom_file', help='Spectrum ROM file')
    parser.add_argument('snapshot_file', help='.SNA-format snapshot file')
    args = parser.parse_args()

    start(args.rom_file, args.snapshot_file)
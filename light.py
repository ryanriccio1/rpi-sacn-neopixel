import sacn
import time
import configparser
from sacnreceiver import SacnUniverse
from pixelstrand import PixelStrand

"""
pixel_array = []
for current_universe in range(4):
    pixel_array.append(PixelStrand('board.D18', 5, 'neopixel.GRB'))

universe_array = []
for current_universe in range(4):
    universe_array.append(SacnUniverse(current_universe + 1, receiver, pixel_array[current_universe]))

time.sleep(10)  # receive for 10 seconds
receiver.stop()
"""


def main():
    receiver = sacn.sACNreceiver()
    receiver.start()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read_file(open(r'config.txt'))

    pixel_pattern = config.get('DMX Out', 'pixel_pattern')
    strand_amount = int(config.get('DMX Out', 'strand_amount'))
    pack_universes = config.getboolean('DMX Out', 'pack_universes')

    strand_dict = {}
    for current_strand in range(1, strand_amount + 1):
        # get config from file
        pin = config.get('DMX Out', f'strand{current_strand}.pin')
        universe_start = config.get('DMX Out', f'strand{current_strand}.universe_start')
        pixel_amount = int(config.get('DMX Out', f'strand{current_strand}.pixels'))

        # init strand dict entry
        strand_dict[f'strand{current_strand}'] = []

        if universe_start == 'auto':
            universe_start = strand_dict[f'strand{current_strand - 1}'][0].get_next_address()['universe']
            addr_start = strand_dict[f'strand{current_strand - 1}'][0].get_next_address()['addr']
        else:
            universe_start = int(universe_start)
            addr_start = 1

        new_strand = PixelStrand(pin, pixel_amount, pixel_pattern, universe_start, addr_start, pack_universes)
        new_strand.calculate_addresses()
        strand_dict[f'strand{current_strand}'].append(new_strand)

        strand_dict[f'strand{current_strand}'].append([new_strand.get_start_universe(), new_strand.get_start_address()])
        strand_dict[f'strand{current_strand}'].append([1, 1]) # [new_strand.get_end_universe(), new_strand.get_end_address()])

    last_universe = strand_dict[f'strand{strand_amount}'][2][0]
    print(last_universe)
    universe_array = []
    for current_universe in range(1, last_universe + 1):
        strands_in_universe = []
        for current_strand in range(1, strand_amount + 1):
            start_universe = strand_dict[f'strand{current_strand}'][1][0]
            end_universe = strand_dict[f'strand{current_strand}'][2][0]
            if start_universe <= current_universe <= end_universe:
                if start_universe == current_universe:
                    if start_universe == end_universe:
                        address_range = [strand_dict[f'strand{current_strand}'][1][1],
                                         strand_dict[f'strand{current_strand}'][2][1]]
                    else:
                        address_range = [strand_dict[f'strand{current_strand}'][1][1], 512]
                elif end_universe == current_universe:
                    address_range = [1, strand_dict[f'strand{current_strand}'][2][1]]
                else:
                    address_range = [1, 512]

                strands_in_universe.append([strand_dict[f'strand{current_strand}'][0], address_range])

        print(f'Current Universe: {current_universe}\t Strands:{strands_in_universe}')
        universe_array.append(SacnUniverse(current_universe, receiver, strands_in_universe))

    print(strand_dict)


if __name__ == '__main__':
    main()

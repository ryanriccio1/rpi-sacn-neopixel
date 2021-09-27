import sacn
import configparser
import atexit
from sacnreceiver import SacnUniverse
from pixelstrand import PixelStrand

receiver = sacn.sACNreceiver()


def main():
    receiver.start()  # main sacn receiver
    atexit.register(exit_cleanup)  # try to clean up before exit

    # try to get config from same directory
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_file(open(r'config.txt'))

    # get config from file
    pixel_pattern = config.get('DMX Out', 'pixel_pattern')  # GRB or RGB
    strand_amount = int(config.get('DMX Out', 'strand_amount'))  # total physical strands
    pack_universes = config.getboolean('DMX Out', 'pack_universes')  # multiple strands per universe = true

    # holds all the physical strands
    strand_dict = {}
    for current_strand in range(1, strand_amount + 1):
        # get config from file per strand
        pin = config.get('DMX Out', f'strand{current_strand}.pin')  # D12, D18, D21 for RPI4
        universe_start = config.get('DMX Out', f'strand{current_strand}.universe_start')  # auto or specific
        pixel_amount = int(config.get('DMX Out', f'strand{current_strand}.pixels'))  # amount on physical strand

        # create a new strand entry (list) in the dictionary
        strand_dict[f'strand{current_strand}'] = []

        # if universe_start is auto, calculate address from previous strand, otherwise just use given universe
        if universe_start == 'auto':
            universe_start = strand_dict[f'strand{current_strand - 1}'][0].get_next_address()['universe']
            addr_start = strand_dict[f'strand{current_strand - 1}'][0].get_next_address()['addr']
        else:
            universe_start = int(universe_start)
            addr_start = 1

        # create strand from new information and add it to our list
        new_strand = PixelStrand(pin, pixel_amount, pixel_pattern, universe_start, addr_start, pack_universes)
        strand_dict[f'strand{current_strand}'].append(new_strand)
        new_strand.get_next_address()

        # store address range for easy use later
        strand_dict[f'strand{current_strand}'].append([new_strand.get_start_universe(), new_strand.get_start_address()])
        strand_dict[f'strand{current_strand}'].append([new_strand.get_end_universe(), new_strand.get_end_address()])

    # get last universe from last strand
    last_universe = strand_dict[f'strand{strand_amount}'][2][0]

    # array of software universes
    universe_array = []

    # loop through each universe, then each strand for each universe
    for current_universe in range(1, last_universe + 1):
        strands_in_universe = []  # new strands_in_universe per universe
        for current_strand in range(1, strand_amount + 1):
            # universe range
            start_universe = strand_dict[f'strand{current_strand}'][0].get_start_universe()
            end_universe = strand_dict[f'strand{current_strand}'][0].get_end_universe()
            address_range = []

            # if current universe in the range of universes in this strand
            if start_universe <= current_universe <= end_universe:
                # if this strand only uses 1 universe
                if start_universe == end_universe:
                    address_range = [strand_dict[f'strand{current_strand}'][0].get_start_address(),
                                     strand_dict[f'strand{current_strand}'][0].get_end_address()]
                else:  # get the info from strand address LUT for current universe
                    address_range = [strand_dict[f'strand{current_strand}'][0].get_universe_start(current_universe),
                                     strand_dict[f'strand{current_strand}'][0].get_universe_end(current_universe)]
                # add to universe
                strands_in_universe.append([strand_dict[f'strand{current_strand}'][0], address_range])

        print(f'Current Universe: {current_universe}\t Strands:{strands_in_universe}')

        # create new software array with current strands_in_universe
        universe_array.append(SacnUniverse(current_universe, receiver, strands_in_universe))

    print(universe_array)


def exit_cleanup():
    # stop everything before exit
    print("Shutting down receiver...")
    receiver.stop()
    print("Done.")


if __name__ == '__main__':
    # try to clean before force quit
    try:
        main()
    except KeyboardInterrupt:
        exit_cleanup()
        exit(0)

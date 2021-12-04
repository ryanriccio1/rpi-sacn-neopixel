import time

import sacn
import os
import traceback
from time import sleep
from sacnreceiver import SacnUniverse
from pixelstrand import PixelStrand
from olareceiver import OlaUniverse
from universe import Universe
from config import Config
from customlogs import Log
from ola.ClientWrapper import ClientWrapper


def main():
    os.system('cp /home/pi/light/autoupdater.py /home/pi/light_starter.py')

    config = Config('config.txt')

    if config.write_logs:
        Log.log_level = config.log_level

    if config.use_ola:
        OlaUniverse.wrapper = ClientWrapper()
        OlaUniverse.client = OlaUniverse.wrapper.Client()
        Log.write_log("Fetching Devices...", Log.LogLevel.LEVEL1)
        Log.write_log("Creating OLA Receiver...", Log.LogLevel.LEVEL3)
        OlaUniverse.client.FetchDevices(OlaUniverse.get_device)
        OlaUniverse.wrapper.Run()
    else:
        Log.write_log("Creating sACN Receiver...", Log.LogLevel.LEVEL3)
        SacnUniverse.client = sacn.sACNreceiver()

    for current_strand in range(1, config.strand_amount + 1):
        config.set_current_strand(current_strand)

        # if universe_start is auto, calculate address from previous strand, otherwise just use given universe
        if config.pin in PixelStrand.used_pins:
            Log.write_log(f"Pin {config.pin} reused!", Log.LogLevel.LEVEL1)
            raise ValueError("Pin Reused!!")

        if config.universe_start == 'auto':
            first_universe = PixelStrand.strands[current_strand - 1].get_next_address()['universe']
            first_addr = PixelStrand.strands[current_strand - 1].get_next_address()['addr']
        else:
            first_universe = int(config.universe_start)
            first_addr = 1

        Log.write_log(f"Used pin {config.pin}.", Log.LogLevel.LEVEL4)
        PixelStrand.used_pins.append(config.pin)

        # create strand from new information and add it to our list
        new_strand = PixelStrand(config.pin, config.pixel_amount, config.pixel_pattern,
                                 first_universe, first_addr, config.pack_universes, pixel_bytes=3,
                                 pixel_offset=config.pixel_offset, export_patch=config.export_patch)
        Log.write_log(f"Created new strand with {config.pixel_amount} "
                      f"pixels on universe {first_universe}.", Log.LogLevel.LEVEL2)
        PixelStrand.strands.append(new_strand)

    Log.write_log(PixelStrand.strands, Log.LogLevel.LEVEL4)
    # get last universe from last strand
    Universe.last_universe = PixelStrand.strands[config.strand_amount].get_end_universe()

    # loop through each universe, then each strand for each universe
    for current_universe in range(1, Universe.last_universe + 1):
        strands_in_universe = []  # new strands_in_universe per universe
        for current_strand in range(1, config.strand_amount + 1):
            # universe range
            start_universe = PixelStrand.strands[current_strand].get_start_universe()
            end_universe = PixelStrand.strands[current_strand].get_end_universe()

            # if current universe in the range of universes in this strand
            if start_universe <= current_universe <= end_universe:
                # if this strand only uses 1 universe
                if start_universe == end_universe:
                    address_range = [PixelStrand.strands[current_strand].get_start_address(),
                                     PixelStrand.strands[current_strand].get_end_address()]
                else:  # get the info from strand address LUT for current universe
                    address_range = [PixelStrand.strands[current_strand].get_universe_start(current_universe),
                                     PixelStrand.strands[current_strand].get_universe_end(current_universe)]
                # add to universe
                strands_in_universe.append([PixelStrand.strands[current_strand], address_range])

        if not strands_in_universe == []:
            Log.write_log(f'Current Universe: {current_universe}\t Strands:{strands_in_universe}', Log.LogLevel.LEVEL2)
            # create new software array with current strands_in_universe
            if config.use_ola:
                Universe.universe_array.append(OlaUniverse(current_universe, strands_in_universe))
            else:
                Universe.universe_array.append(SacnUniverse(current_universe, strands_in_universe))

    Log.write_log(Universe.universe_array, Log.LogLevel.LEVEL4)

    if config.use_ola:
        Log.write_log("OLA Receiver Started.", Log.LogLevel.LEVEL2)
        OlaUniverse.wrapper.Run()
    else:
        Log.write_log("sACN Receiver Started.", Log.LogLevel.LEVEL2)
        SacnUniverse.client.start()


if __name__ == '__main__':
    try:
        main()
    except:
        Log.write_log(traceback.format_exc(), Log.LogLevel.LEVEL1)
        exit(1)

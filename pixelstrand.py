import neopixel
import board


class PixelStrand(object):
    def __init__(self, pin=board.D12, amount=5, pattern=neopixel.GRB, start_universe=1, start_address=1,
                 pack_universes=False, pixel_bytes=3):
        """
        NeoPixel strand constructor

        :param pin: The physical pin on the RPI
        :type pin: board.PIN
        :param amount: The physical amount of pixels on a physical strand
        :type amount: int
        :param pattern: NeoPixel pattern ex. RGB and GRB
        :type pattern:  neopixel.PATTERN
        :param start_universe: Starting software universe of strand
        :type start_universe: int
        :param start_address: Starting software address of strand
        :type start_address: int
        :param pack_universes: Allow multiple strands per software universe
        :type pack_universes: bool
        :param pixel_bytes: Number of bytes used per pixel ex. RGB = 3, RGBW = 4
        :type pixel_bytes: int

        :return: None
        """
        # LUT given strand and associate with neopixel enum
        self._pin_dict = {
            'board.D10': board.D10,
            'board.D12': board.D12,
            'board.D18': board.D18,
            'board.D21': board.D21
        }
        self._pattern_dict = {
            'neopixel.GRB': neopixel.GRB,
            'neopixel.RGB': neopixel.RGB
        }

        # lookup and associate with class enum
        self._pin = self._pin_dict[pin]
        self._pattern = self._pattern_dict[pattern]

        # create protected members
        self._amount = amount
        self._start_universe = start_universe
        self._start_address = start_address
        self._pack_universes = pack_universes  # share universe between strand
        self._pixel_bytes = pixel_bytes  # ex. RGB = 3, RGBW = 4

        # address "patch" for strand
        self._address_dict = {}

        self.calculate_addresses()  # fill "patch" and create neopixel strand
        self._pixels = neopixel.NeoPixel(self._pin, 5, brightness=0.2, auto_write=False, pixel_order=self._pattern)

    def write(self, dmx, universe, address_start, address_end):
        """
        Write to physical strand given DMX packet

        :param dmx: A dmx packet
        :type dmx: packet.dmxData
        :param universe: Universe source
        :type universe: int
        :param address_start: Starting address in universe
        :type address_start: int
        :param address_end: Ending address in universe
        :type address_end: int

        :return: None
        """
        # loop through each pixel in the amount of pixels in universe
        for pixel_index in range(int((address_end - address_start) / 3) + 1):
            # lookup and offset packet index from "patch"
            byte1 = self._address_dict[universe][pixel_index][1] - 1
            byte2 = byte1 + 1
            byte3 = byte1 + 2
            print((dmx[byte1], dmx[byte2], dmx[byte3]))
            self._pixels[pixel_index] = (dmx[byte1], dmx[byte2], dmx[byte3])
        self._pixels.show()

    def calculate_addresses(self):
        """
        Calculate address and write to patch

        :return: None
        """
        addr = self._start_address
        univ = self._start_universe
        address_table = {
            univ: []
        }
        # loop through each pixel and write to address_dict
        for pixel in range(self._amount):
            # if the next pixel will overflow a universe
            if addr + self._pixel_bytes > 512:
                # start at 1 again and increase univ
                addr = 1
                univ += 1
                # add a new list of pixels in new universe
                address_table[univ] = []
            # append pixel and then go to next pixel
            address_table[univ].append([pixel + 1, addr])
            addr += self._pixel_bytes

        # make it a class member
        self._address_dict = address_table

    def get_next_address(self):
        """
        Get starting address of upcoming strand

        :return: dict{'universe': universe, 'addr': addr}
        """
        # calculate starting address of next strand
        if self._pack_universes:
            next_univ, next_addr = 1, 1
            # if the next pixel is an overflow, go to next universe
            if self.get_end_address() + self._pixel_bytes > 512:
                next_univ = self.get_end_universe() + 1
            else:  # get next address if not overflow
                next_univ = self.get_end_universe()
                next_addr = self.get_end_address() + 1
            return {'universe': next_univ, 'addr': next_addr}
        else:  # just give it the next universe
            return {'universe': self.get_end_universe() + 1, 'addr': 1}

    def get_start_universe(self):
        """
        :return: int Starting universe of entire strand
        """
        return self._start_universe

    def get_start_address(self):
        """
        :return: int Starting address of first universe
        """
        return self._start_address

    def get_end_universe(self):
        """
        :return: int Ending universe of entire strand
        """
        # lookup last dict key and use this as the ending universe
        # NOTE: since Python 3.7, dicts default to being ordered
        return list(self._address_dict.keys())[-1]

    def get_end_address(self):
        """
        :return: int Ending address of last universe in strand
        """
        # get last pixel on last universe, and get starting address plus pixel_bytes not including
        # the starting address
        return list(self._address_dict.values())[-1][-1][1] + self._pixel_bytes - 1

    def get_universe_start(self, universe):
        """
        Lookup address in "patch" given universe

        :param universe: Universe to lookup
        :type universe: int

        :return: int Starting address of given universe
        """
        # lookup first pixel in given universe
        return self._address_dict[universe][0][1]

    def get_universe_end(self, universe):
        """
        Lookup address in "patch" given universe

        :param universe: Universe to lookup
        :type universe: int

        :return: int Ending address of given universe
        """
        # lookup last address in last pixel of given universe plus pixel_bytes not including
        # the starting address
        return self._address_dict[universe][-1][1] + self._pixel_bytes - 1
